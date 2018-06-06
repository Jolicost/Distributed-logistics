
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

from Util.Namespaces import *
from Util.GestorDirecciones import formatDir
from rdflib.namespace import RDF
from rdflib import Graph, Namespace, Literal,BNode

__author__ = 'javier'


# Configuration stuff. En principio hay que imaginar que mecanismo se utilizara 
# Para contactar con los vendedores externos
host = 'localhost'
port = 8003

#Direccion del directorio que utilizaremos para obtener las direcciones de otros agentes
directorio_host = 'localhost'
directorio_port = 9000

#Hardcoding de los empaquetadores
empaquetador = getNamespace('AgenteEmpaquetador')

agn = getAgentNamespace()

receptor = getNamespace('AgenteReceptor')
#Objetos agente
AgenteReceptor = Agent('AgenteAdmisor',receptor['generic'],formatDir(host,port) + '/comm',None)
DirectorioAgentes = Agent('DirectorioAgentes',agn.Directory,formatDir(directorio_host,directorio_port) + '/comm',None)

productos_ns = getNamespace('Productos')
pedidos_ns = getNamespace('Pedidos')

productos_db = 'Datos/productos.turtle'
productos = Graph()

pedidos_db = 'Datos/pedidos.turtle'
pedidos = Graph()

direcciones_ns = getNamespace('Direcciones')

cola1 = Queue()

# Flask stuff
app = Flask(__name__,template_folder="AgenteReceptor/templates")

#Acciones. Este diccionario sera cargado con todos los procedimientos que hay que llamar dinamicamente 
# cuando llega un mensaje
actions = {}

#Carga los grafoos rdf de los distintos ficheros
def cargarGrafos():
	global productos
	productos = Graph()
	pedidos = Graph()
	if os.path.isfile(productos_db):
		productos.parse(productos_db,format="turtle")
	if os.path.isfile(pedidos_db):
		pedidos.parse(pedidos_db,format="turtle")

def guardarGrafo(g,file):
	g.serialize(file,format="turtle")	

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


@app.route("/")
def main():
	"""
	Pagina principal. Contiene un menu muy simple
	"""
	return render_template('main.html')

@app.route("/anadir")
def anadirPedido():
	''' Muestra la pagina de anadir un nuevo pedido '''
	return render_template('nuevoPedido.html')


@app.route("/crearPedido")
def crearPedido():
	'''
	Crear un pedido mediante los atributos que se mandan en el http request
	'''
	attrs = request.args
	id = attrs['id']
	user_id = attrs['user_id']
	fecha = attrs['date']
	prioridad = attrs['priority']
	direccion = attrs['direction']
	cp = attrs['cp']
	direccion_id = direccion + cp

	#Nodo padre y su tipo
	pedidos.add((pedidos_ns[id],RDF.type,pedidos_ns.type))

	#Anadimos el nodo de la direccion con su tipo y todo
	pedidos.add((direcciones_ns[direccion_id],RDF.type,direcciones_ns.type))
	pedidos.add((direcciones_ns[direccion_id],direcciones_ns.Direccion,Literal(direccion)))
	pedidos.add((direcciones_ns[direccion_id],direcciones_ns.Codigopostal,Literal(cp)))
	#Enlazamos la direccion con el pedido
	pedidos.add((pedidos_ns[id],pedidos_ns.Tienedirecciondeentrega,direcciones_ns[direccion_id]))

	pedidos.add((pedidos_ns[id],pedidos_ns.Fecharealizacion,Literal(fecha)))
	pedidos.add((pedidos_ns[id],pedidos_ns.Prioridad,Literal(prioridad)))
	pedidos.add((pedidos_ns[id],pedidos_ns.Hechopor,Literal(user_id)))

	guardarGrafo(pedidos,pedidos_db)

	return redirect("/")

def decidirResponsabilidadEnvio(pedido):
	pass
def informarResponsabilidadEnvio(pedido):
	''' 
	Envia un mensaje al vendedor del producto si este era ofrecido por ellos. 
	'''
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
	pass


def agentbehavior1(cola):
	"""
	Un comportamiento del agente

	:return:
	"""
	pass


def registerActions():
	global actions
	#actions[agn.VendedorNuevoProducto] = nuevoProducto

'''Percepciones'''
def peticionDeCompra(graph):
	pass


if __name__ == '__main__':
	# Ponemos en marcha los behaviors
	ab1 = Process(target=agentbehavior1, args=(cola1,))
	ab1.start()

	registerActions()

	cargarGrafos()
	# Ponemos en marcha el servidor
	app.run(host=host, port=port,debug=True)

	# Esperamos a que acaben los behaviors
	ab1.join()
	print('The End')


