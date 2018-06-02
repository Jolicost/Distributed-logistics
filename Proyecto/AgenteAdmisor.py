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

from Datos.Namespaces import getNamespace,getAgentNamespace
from Util.GestorDirecciones import formatDir

__author__ = 'javier'


# Configuration stuff
host = 'localhost'
port = 8001

vendedor_host = 'localhost'
vendedor_port = 8000

agn = Namespace(getAgentNamespace())
#Objetos agente
AgenteAdmisor = Agent('AgenteAdmisor',agn.admisor,formatDir(host,port) + '/comm',None)
AgenteVendedorExterno = Agent('AgenteVendedorExterno',agn.vendedor,formatDir(vendedor_host,vendedor_port) + '/comm',None)

productos = getNamespace('Productos')

# Contador de mensajes
mss_cnt = 0

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
	gr = build_message(Graph(),ACL.confirm,sender=AgenteAdmisor.uri)
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
	app.run(host=host, port=port)

	# Esperamos a que acaben los behaviors
	ab1.join()
	print('The End')


