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

# Configuration stuff
#hostname = socket.gethostname()
hostname = 'localhost'
port = 9010

logger = config_logger(level=1, file="agentemonetario")

agn = Namespace("http://www.agentes.org#")

# Contador de mensajes
mss_cnt = 0

# Datos del Agente

AgenteMonetario = Agent('AgenteMonetario',
                       agn.AgenteMonetario,
                       'http://%s:%d/comm' % (hostname, port),
                       'http://%s:%d/Stop' % (hostname, port))

# Directory agent address
DirectoryAgent = Agent('DirectoryAgent',
                       agn.Directory,
                       'http://%s:9000/Register' % hostname,
                       'http://%s:9000/Stop' % hostname)


# Global triplestore graph
dsgraph = Graph()

cola1 = Queue()

# Flask stuff
app = Flask(__name__)


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
                sender=InfoAgent.uri,
                msgcnt=mss_cnt,
                receiver=msgdic['sender'], 
                mss_cnt=mss_cnt)

            #iniciar proceso de pago
            ab1 = Process(target=pedir_pago, args=(cola1,))
            ab1.start()

            
        mss_cnt += 1
        print ("Respuesta enviada")

        return gr.serialize(format='xml')


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

def pedir_pago(cola):


    pass

def agentbehavior1(cola):
    """
    Un comportamiento del agente
    :return:
    """

    pass


if __name__ == '__main__':
    # Ponemos en marcha los behaviors
    #ab1 = Process(target=agentbehavior1, args=(cola1,))
    #ab1.start()

    # Ponemos en marcha el servidor
    app.run(host=hostname, port=port)

    # Esperamos a que acaben los behaviors
    #ab1.join()
    print('The End')