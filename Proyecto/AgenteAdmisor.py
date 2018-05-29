# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 15:58:13 2013

Esqueleto de agente usando los servicios web de Flask

/comm es la entrada para la recepcion de mensajes del agente
/Stop es la entrada que para el agente

Tiene una funcion AgentBehavior1 que se lanza como un thread concurrente

Asume que el agente de registro esta en el puerto 9000

@author: javier
"""

from __future__ import print_function
from multiprocessing import Process, Queue
import socket

from rdflib import Namespace, Graph
from flask import Flask, request, render_template,redirect
from Util.ACLMessages import build_message, get_message_properties, send_message
from Util.OntoNamespaces import ACL, DSO
from Util.FlaskServer import shutdown_server
from Util.Agente import Agent
__author__ = 'javier'


# Configuration stuff
hostname = socket.gethostname()
port = 9010

productos = Namespace("http://www.tienda.org/productos#")

agn = Namespace("http://www.agentes.org#")

# Contador de mensajes
mss_cnt = 0

# Datos del Agente

AgentePersonal = Agent('AgenteSimple',
					   agn.AgenteSimple,
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

@app.route("/")
def hola():
	return "soy el agente admisor, hola!"

@app.route("/altaProducto")
def altaProducto():
	pass




@app.route("/comm")
def comunicacion():
	"""
	Entrypoint de comunicacion
	"""
	mess = request.args['content']
	print(mess)
	#hay que responder que si no lanza excepcion
	gr = build_message(Graph(),ACL.confirm,sender=AgentePersonal.uri)
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
	pass


def agentbehavior1(cola):
	"""
	Un comportamiento del agente

	:return:
	"""
	pass


if __name__ == '__main__':
	# Ponemos en marcha los behaviors
	ab1 = Process(target=agentbehavior1, args=(cola1,))
	ab1.start()

	# Ponemos en marcha el servidor
	app.run(host=hostname, port=port)

	# Esperamos a que acaben los behaviors
	ab1.join()
	print('The End')


