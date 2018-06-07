
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
from Util.ACLMessages import *
from Util.OntoNamespaces import ACL, DSO
from Util.FlaskServer import shutdown_server
from Util.Agente import Agent
from Util.Directorio import *
from Util.Namespaces import *
from Util.GraphUtil import *
from Util.ModelParser import *
from Util.GestorDirecciones import formatDir
from rdflib.namespace import RDF
from rdflib import Graph, Namespace, Literal,BNode
from rdflib.collection import Collection

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
vendedores_ns = getNamespace('AgenteVendedorExterno')
usuarios_ns = getNamespace('AgenteUsuario')

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

def initAgent():
	register_message(AgenteReceptor,DirectorioAgentes,receptor.type)
#Carga los grafoos rdf de los distintos ficheros
def cargarGrafos():
	global productos
	global pedidos
	productos = Graph()
	pedidos = Graph()
	if os.path.isfile(productos_db):
		productos.parse(productos_db,format="turtle")
	if os.path.isfile(pedidos_db):
		pedidos.parse(pedidos_db,format="turtle")

def guardarGrafo(g,file):
	g.serialize(file,format="turtle")	

def guardarGrafoPedidos():
	pedidos.serialize(pedidos_db,format="turtle")

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

@app.route("/info")
def info():
	list = [productos,pedidos]
	list = [g.serialize(format="turtle") for g in list]
	return render_template("info.html",list=list)

@app.route("/anadir")
def anadirPedido():
	''' Muestra la pagina de anadir un nuevo pedido '''
	return render_template('nuevoPedido.html')



@app.route("/verPedidos")
def verPedidos():
	list = []

	#obtenemos todos los pedidos de la tienda
	pds = pedidos.subjects(predicate=RDF.type,object=pedidos_ns.type)

	for p in pds:
		dict = pedido_a_dict(pedidos,p)
		list+= [dict]

	return render_template('listaPedidos.html',list=list)

@app.route("/crearPedido")
def crearPedido():
	'''
	Crear un pedido mediante los atributos que se mandan en el http request
	'''
	dict = request.args
	g = dict_a_pedido(dict)
	global pedidos
	pedidos+=g
	guardarGrafo(pedidos,pedidos_db)

	return redirect("/")

@app.route("/pedidos/<id>/anadirProductoPedido")
def anadirProductoPedido(id):
	'''
	crea la vista para anadir un producto a un pedido en concreto
	'''
	return render_template('nuevoProductoPedido.html',id=id)

@app.route("/pedidos/<id>/crearProductoPedido")
def crearProductoPedido(id):
	''' anade un producto a un pedido en especifico '''
	global pedidos
	pedido = pedidos_ns[id]

	producto_id = request.args['id']
	estado = request.args['estado']

	g = Graph()
	prod_parent = productos_ns[producto_id]
	g.add((prod_parent,RDF.type,productos_ns.type))
	g.add((prod_parent,productos_ns.Id,Literal(producto_id)))
	g.add((prod_parent,productos_ns.EstadoProducto,Literal(estado)))

	pedidos += g

	node = productos.value(subject=pedido,predicate=pedidos_ns.Contiene) or pedidos_ns.lista
	pedidos.add((pedido,pedidos_ns.Contiene,node))
	c = Collection(pedidos,node)
	c.append(prod_parent)
	#Modificar la coleccion de productos del pedido
	guardarGrafoPedidos()
	return redirect("/verPedidos")

@app.route("/pedidos/<id>/verProductos")
def verProductosPedido(id):

	# Busca toda la informacion que cuelga de pedidos
	pedido = expandirGrafoRec(pedidos,pedidos_ns[id])


@app.route("/simularPedido")
def simularPedido():
	'''
	simula un pedido que ha llegado a la tienda. Utiliza el propio pedido
	notifica a la tienda externa que el pedido sera llevado a cabo por ellos
	'''
	id = request.args['id']

	responsabilidad = decidirResponsabilidadEnvio(pedidos_ns[id])

	pedido = expandirGrafoRec(pedidos,pedidos_ns[id])

	responsable = responsabilidad['responsabilidad']

	obj = createAction(AgenteReceptor,'informarResponsabilidad')
	#Anadimos la accion del mensaje
	pedido.add((obj,RDF.type,agn.ReceptorInformarResponsabilidad))
	#Indicamos si el receptor es el responsable o no del pedido
	pedido.add((obj,pedidos_ns.responsable,Literal(responsable)))
	msg = build_message(pedido,
		perf=ACL.inform,
		sender=AgenteReceptor.uri,
		content=obj)

	print(responsabilidad)
	send_message_set(msg,AgenteReceptor,DirectorioAgentes,vendedores_ns.type,responsabilidad['vendedores'])
	return redirect("/verPedidos")

def productoPerteneceTiendaExterna(producto):
	vendedor = productos.value(subject=producto,predicate=productos_ns.Esvendidopor)
	if (vendedor): return vendedor
	else: return False

def decidirResponsabilidadEnvio(pedido):
	'''
	Devuelve True si el envio es responsabilidad del vendedor externo
	Devuelve False si el envio es responsabilidad de la tienda
	'''
	container = pedidos.value(subject=pedido,predicate=pedidos_ns.Contiene)
	c = Collection(pedidos,container)
	vendedores = []
	pertenecen = 0
	i = 0
	for item in c:
		#Iteramos los productos del pedido
		prod_id = pedidos.value(subject=item,predicate=productos_ns.Id)
		vendedor = productoPerteneceTiendaExterna(productos_ns[prod_id])
		if (vendedor):
			vendedores += [vendedor]
			pertenecen += 1
		i+=1

	#Eliminamos los duplicados
	vendedores = list(set(vendedores))
	#Solo hay que asignar la responsabilidad al vendedor externo si este es el propietario 
	#De todos los productos del envio
	envioExterno = len(vendedores) == 1
	ret = {
		'responsabilidad':envioExterno,
		'vendedores':vendedores
	}
	return ret
	#Si todos pertenecen entonces i == pertenecen

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

	initAgent()
	registerActions()

	cargarGrafos()

	# Ponemos en marcha el servidor
	app.run(host=host, port=port,debug=True)

	# Esperamos a que acaben los behaviors
	ab1.join()
	print('The End')


