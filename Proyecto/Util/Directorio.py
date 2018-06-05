from __future__ import print_function
from multiprocessing import Process, Queue
import socket
import argparse

from flask import Flask, request
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import FOAF, RDF

from OntoNamespaces import ACL, DSO
from ACLMessages import *
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

def directory_search_specific(agentSender,directoryAgent,type,uri):
	"""
	Busca un agente del tipo type y con la uri especificada en el servicio de directorio
	"""
	gmess = Graph()
	gmess.bind('foaf', FOAF)
	gmess.bind('dso', DSO)
	reg_obj = createAction(agentSender,'search-specific')
	gmess.add((reg_obj, RDF.type, DSO.SearchSpecific))
	gmess.add((reg_obj, DSO.AgentType, type))
	gmess.add((reg_obj, DSO.AgentUri, uri))

	msg = build_message(gmess, perf=ACL.request,
						sender=agentSender.uri,
						receiver=directoryAgent.uri,
						content=reg_obj)
	gr = send_message(msg, directoryAgent.address)
	return gr

def directory_search_global(agentSender,directoryAgent,type):
	"""
	Busca un agente del tipo type y con la uri especificada en el servicio de directorio
	"""
	gmess = Graph()
	gmess.bind('foaf', FOAF)
	gmess.bind('dso', DSO)
	reg_obj = createAction(agentSender,'search-global')
	gmess.add((reg_obj, RDF.type, DSO.SearchGlobal))
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
	parse = parse_message(res,performative=ACL.inform)
	if not parse:
		raise Exception('Agente no encontrado')
   
	node = parse['msgdic']['content']   
	address = res.objects(node,DSO.Address).next()
	return send_message(msg,address)

def send_message_uri(msg,agentSender,directoryAgent,type,uri):

	res = directory_search_specific(agentSender,directoryAgent,type,uri)
	parse = parse_message(res,performative=ACL.inform)
	if not parse:
		raise Exception('Agente no encontrado')

	node = parse['msgdic']['content']
	address = res.objects(node,DSO.Address).next()
	return send_message(msg,address)

def send_message_all(msg,agentSender,directoryAgent,type):
	
	res = directory_search_global(agentSender,directoryAgent,type)
	agentes = res.subjects(predicate=DSO.Type,object=DSO.Agent)
	responses = []
	for agente in agentes:
		address = res.objects(subject=agente,predicate=DSO.Address).next()
		responses += [
			{
			"uri":agente,
			"msg":send_message(msg,address)
			}
		]
	return responses