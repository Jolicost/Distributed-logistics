from __future__ import print_function
from Agente import Agente
from FlaskServer import shutdown_server
from multiprocessing import Process, Queue
import socket

from rdflib import Namespace, Graph, Literal
from flask import Flask, request
from ACLMessages import build_message, send_message, get_message_properties
from OntoNamespaces import ACL, DSO
from rdflib.namespace import FOAF
from Logging import config_logger
import json
import logging
from datetime import datetime, timedelta

#Cambiamos la ruta por defecto de los templates para que sea dentro de los ficheros del agente
app = Flask(__name__,template_folder="AgenteVendedorExterno/templates")
agn = None 
AgenteMonetario = None 
ServicioPago = None
host = None
port = None
g = None
#Espacio de nombres para los productos y los agentes
agn = Namespace("http://www.agentes.org#")

# Datos del Agente

def init_agent():
    dir = GestorDirecciones.getDirAgenteMonetario()
    global host,port,agn,g,AgenteMonetario,ServicioPago
    host = dir['host']
    port = dir['port']
    agn = Namespace("http://www.agentes.org#")
    g = cargarGrafo()
    AgenteMonetario = Agent('AgenteMonetario',agn.AgenteMonetario,'localhost:9010/comm','localhost:9010/stop')
    ServicioPago = Agent('ServicioPago',agn.ServicioPago,'localhost:9020/comm','localhost:9010/stop')


@app.route("/comm")
def comunicacion():
    """
    Entrypoint de comunicacion
    """
    global dsgraph
    global mss_cnt

    print ('Peticion de informacion recibida\n')

    # Extraemos el mensaje y creamos un grafo con el
    message = request.args['content']
    print ("Mensaje extraído\n")
    # VERBOSE
    print ("\n\n")
    gm = Graph()
    gm.parse(data=message)
    print ('Grafo creado con el mensaje')

    msgdic = get_message_properties(gm)

    # Comprobamos que sea un mensaje FIPA ACL
    if msgdic is None:
        # Si no es, respondemos que no hemos entendido el mensaje
        gr = build_message(Graph(), ACL['not-understood'], sender=AgenteMonetario.uri, msgcnt=mss_cnt)
        print ('El mensaje no era un FIPA ACL')
    else:
        # Obtenemos la performativa
        perf = msgdic['performative']

        if perf != ACL.request:
            # Si no es un request, respondemos que no hemos entendido el mensaje
            gr = build_message(Graph(), ACL['not-understood'], sender=AgenteMonetario.uri, msgcnt=mss_cnt)
        else:
            # Extraemos el objeto del contenido que ha de ser una accion de la ontologia de acciones del agente
            # de registro

            # Averiguamos el tipo de la accion
            if 'content' in msgdic:
                content = msgdic['content']
                accion = gm.value(subject=content, predicate=RDF.type)

            gr = build_message(Graph(),
                perf=ACL['inform-done'],
                sender=AgenteMonetario.uri,
                msgcnt=mss_cnt,
                receiver=msgdic['sender'], 
                mss_cnt=mss_cnt)

            #hacemos accion dependiendo del tipo
            ont = Namespace('/Ontologias/ontologies.owl')
            if (accion == ont.Pedirpagousuario):
                ab1 = Process(target=pedir_pago_usuario, args=(cola1,))
            elif (accion == ont.Pagarvendederexterno):
                ab1 = Process(target=pagar_vendedor_externo, args=(cola1,))
            else:
                gr = build_message(Graph(),
                ACL['not-understood'],
                sender=AgenteMonetario.uri,
                msgcnt=mss_cnt)

            #iniciar proceso de pago
            ab1.start()

            
        mss_cnt += 1
        print ("Respuesta enviada")

        return gr.serialize(format='xml')

def pedir_pago_usuario(cola):
    global mss_cnt
    logger.info("Hacemos una petición de pago al servicio de pago")
    gmess = Graph()

    #ontologias
    ont = Namespace('/Ontologias/ontologies.owl')

    gmess.bind(ont)
    reg_obj = agn[AgenteMonetario.name]
    gmess.add((reg_obj, RDF.type, ont.Pedirpagousuario))

    msg = build_message(gmess, perf=ACL.request,
        sender=AgenteMonetario.uri,
        receiver=ServicioPago.uri,
        msgcnt=mss_cnt)
    gr = send_message(msg, addr)
    mss_cnt
    logger.info("Recibimos respuesta a la petición")
    return gr

    pass

def pagar_vendedor_externo(cola):       
    global mss_cnt
    logger.info("Hacemos una petición de pago al servicio de pago")
    gmess = Graph()

    #ontologias
    ont = Namespace('/Ontologias/ontologies.owl')

    gmess.bind(ont)
    reg_obj = agn[AgenteMonetario.name]
    gmess.add((reg_obj, RDF.type, ont.Pagarvendederexterno))

    msg = build_message(gmess, perf=ACL.request,
        sender=AgenteMonetario.uri,
        receiver=ServicioPago.uri,
        msgcnt=mss_cnt)
    gr = send_message(msg, addr)
    mss_cnt
    logger.info("Recibimos respuesta a la petición")
    return gr

    pass

@app.route("/Stop")
def stop():
    """
    Entrypoint que para el agente
    :return:
    """
    tidyup()
    shutdown_server()
    return "Parando Servidor"


def tidyup():
    """
    Acciones previas a parar el agente
    """
    global cola1
    cola1.put(0)
    pass

def agentbehavior1(cola):
    """
    Un comportamiento del agente
    :return:
    """

    pass


def start_server():
    init_agent()
    app.run()


if __name__ == "__main__":
    start_server()
