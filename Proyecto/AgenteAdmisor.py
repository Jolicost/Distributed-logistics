
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
import os.path

from rdflib import Namespace, Graph
from flask import Flask, request, render_template,redirect
from Util.ACLMessages import build_message, get_message_properties, send_message, create_confirm, create_notUnderstood
from Util.OntoNamespaces import ACL, DSO
from Util.FlaskServer import shutdown_server
from Util.Agente import Agent

from Datos.Namespaces import getNamespace,getAgentNamespace
from Util.GestorDirecciones import formatDir
from rdflib.namespace import RDF

__author__ = 'javier'


# Configuration stuff. En principio hay que imaginar que mecanismo se utilizara 
# Para contactar con los vendedores externos
host = 'localhost'
port = 8001




agn = getAgentNamespace()

admisor = getNamespace('AgenteAdmisor')
#Objetos agente
AgenteAdmisor = Agent('AgenteAdmisor',admisor['generic'],formatDir(host,port) + '/comm',None)

productos_ns = getNamespace('Productos')

productos_db = 'Datos/productos.turtle'
productos = Graph()

cola1 = Queue()

# Flask stuff
app = Flask(__name__)

#Acciones. Este diccionario sera cargado con todos los procedimientos que hay que llamar dinamicamente 
# cuando llega un mensaje
actions = {}

#Carga los grafoos rdf de los distintos ficheros
def cargarGrafos():
	global productos
	productos = Graph()
	if os.path.isfile(productos_db):
		productos.parse(productos_db,format="turtle")
	

def guardarGrafo(g,file):
	g.serialize(file,format="turtle")	

@app.route("/")
def hola():
	return "soy el agente admisor, hola!"

@app.route("/altaProducto")
def altaProducto():
	return 'ruta no definida'


def nuevoProducto(graph):
	#TODO hay que generar una lista de centros logisticos que tienen este producto (lo generamos aleatoreamente?)
	global productos
	p = graph.subjects(predicate=RDF.type,object=productos_ns.type)
	for pe in p:
		productos += graph.triples((pe,None,None))
	productos = productos + graph
	guardarGrafo(productos,productos_db)
	return create_confirm(AgenteAdmisor,None)


@app.route("/comm")
def comunicacion():

	# Extraemos el mensaje y creamos un grafo con él
	message = request.args['content']
	gm = Graph()
	gm.parse(data=message)

	msgdic = get_message_properties(gm)

	print(message)
	# Comprobamos que sea un mensaje FIPA ACL y que la performativa sea correcta
	if not msgdic or msgdic['performative'] != ACL.request:
		# Si no es, respondemos que no hemos entendido el mensaje
		gr = create_notUnderstood(AgenteAdmisor,None)
	else:
		content = msgdic['content']
		# Averiguamos el tipo de la accion
		accion = gm.value(subject=content, predicate=RDF.type)

		#Llamada dinamica a la accion correspondiente
		if accion in actions:
			gr = actions[accion](gm)
		else:
			gr = create_notUnderstood(AgenteAdmisor,None)

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


def registerActions():
	global actions
	actions[agn.VendedorNuevoProducto] = nuevoProducto



if __name__ == '__main__':
	# Ponemos en marcha los behaviors
	ab1 = Process(target=agentbehavior1, args=(cola1,))
	ab1.start()

	registerActions()

	cargarGrafos()
	# Ponemos en marcha el servidor
	app.run(host=host, port=port)

	# Esperamos a que acaben los behaviors
	ab1.join()
	print('The End')


