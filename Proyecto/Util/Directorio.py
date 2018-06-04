from __future__ import print_function
from multiprocessing import Process, Queue
import socket
import argparse

from flask import Flask, request
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import FOAF, RDF

from OntoNamespaces import ACL, DSO
from ACLMessages import build_message, send_message, get_message_properties
from Agente import Agent
from Logging import config_logger
from Namespaces import createAction

def register_message(agentSender,directoryAgent,agentType):
    """
    Envia un mensaje de registro al servicio de registro
    usando una performativa Request y una accion Register del
    servicio de directorio

    :param gmess:
    :return:
    """
    gmess = Graph()

    # Construimos el mensaje de registro
    gmess.bind('foaf', FOAF)
    gmess.bind('dso', DSO)
    reg_obj = createAction(agentSender,'register')
    gmess.add((reg_obj, RDF.type, DSO.Register))
    gmess.add((reg_obj, DSO.Uri, agentSender.uri))
    gmess.add((reg_obj, FOAF.Name, Literal(agentSender.name)))
    gmess.add((reg_obj, DSO.Address, Literal(agentSender.address)))
    gmess.add((reg_obj, DSO.AgentType, agentType))

    # Lo metemos en un envoltorio FIPA-ACL y lo enviamos
    gr = send_message(
        build_message(gmess, perf=ACL.request,
                      sender=agentSender.uri,
                      receiver=directoryAgent.uri,
                      content=reg_obj),
        directoryAgent.address)
    return gr



def directory_search_message(agentSender,directoryAgent,type):
    """
    Busca en el servicio de registro mandando un
    mensaje de request con una accion Seach del servicio de directorio

    Podria ser mas adecuado mandar un query-ref y una descripcion de registo
    con variables

    :param type:
    :return:
    """
    gmess = Graph()

    gmess.bind('foaf', FOAF)
    gmess.bind('dso', DSO)
    reg_obj = createAction(agentSender,'search')
    gmess.add((reg_obj, RDF.type, DSO.Search))
    gmess.add((reg_obj, DSO.AgentType, type))

    msg = build_message(gmess, perf=ACL.request,
                        sender=agentSender.uri,
                        receiver=directoryAgent.uri,
                        content=reg_obj)
    gr = send_message(msg, directoryAgent.address)
    return gr


def send_message_any(msg,agentSender,directoryAgent,type):
    ''' buscar un receptor i enviar missatge '''
    res = directory_search_message(agentSender,directoryAgent,type)
    dic = get_message_properties(res)
    node = dic['content']
    address = res.objects(node,DSO.Address).next()
    print(address)
    return send_message(msg,address)

def send_message_uri(agentSender,directoryAgent,type,uri):
    pass

def send_message_all(agentSender,directoryAgent,type):
    pass