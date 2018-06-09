from __future__ import print_function
from multiprocessing import Process
import os.path
#Clase agente
from Util.Agente import Agent
#Renders del flask
from flask import Flask, request, render_template,redirect
from time import sleep
#Funciones para recuperar las direcciones de los agentes
from Util.GestorDirecciones import formatDir
from Util.ACLMessages import build_message, get_message_properties, send_message
from Util.OntoNamespaces import ACL, DSO
from Util.Directorio import *
#Diccionario con los espacios de nombres de la tienda
from Util.Namespaces import *
#Utilidades de RDF
from rdflib import Graph, Namespace, Literal,BNode
from rdflib.namespace import FOAF, RDF
from Util.GraphUtil import *
from rdflib.collection import Collection


import random

app = Flask(__name__,template_folder="AgenteEmpaquetador/templates")

#Direcciones hardcodeadas (propia)
host = 'localhost'
port = 8010

centroLogistico = 'vallecas'

directorio_host = 'localhost'
directorio_port = 9000

agn = getAgentNamespace()

envios = Graph()
lotes = Graph()
pesos = Graph()

envios_db = 'Datos/Envios/%s.turtle'
lotes_db = 'Datos/Lotes/%s.turtle'
pesos_db = 'Datos/Pesos/%s.turtle'

#Objetos agente, no son necesarios en toda regla pero sirven para agilizar comunicaciones
AgenteEmpaquetador = Agent('AgenteEmpaquetador',getNamespace('AgenteEmpaquetador')[centroLogistico],formatDir(host,port) + '/comm',None)
DirectorioAgentes = Agent('DirectorioAgentes',agn.Directory,formatDir(directorio_host,directorio_port) + '/comm',None)
#Cargar el grafo de datos

#Acciones. Este diccionario sera cargado con todos los procedimientos que hay que llamar dinamicamente
# cuando llega un mensaje
actions = {}

#Carga el grafo rdf del fichero graphFile
def cargarGrafos(centro):
	global envios,lotes,pesos
	if os.path.isfile(envios_db%centro):
		envios.parse(envios_db%centro,format="turtle")
	if os.path.isfile(lotes_db%centro):
		lotes.parse(lotes_db%centro,format="turtle")
	if os.path.isfile(pesos_db%centro):
		pesos.parse(pesos_db%centro,format="turtle")

def guardarGrafoEnvios(centro):
	envios.serialize(envios_db%centro,format="turtle")

def guardarGrafoLotes(centro):
	lotes.serialize(lotes_db%centro,format="turtle")

def guardarGrafoPesos(centro):
	pesos.serialize(pesos_db%centro,format="turtle")

@app.route("/comm")
def comunicacion():
	# Extraemos el mensaje y creamos un grafo con el
	message = request.args['content']
	gm = Graph()
	gm.parse(data=message)

	msgdic = get_message_properties(gm)
	gr = None
	# Comprobamos que sea un mensaje FIPA ACL y que la performativa sea correcta
	if not msgdic:
		# Si no es, respondemos que no hemos entendido el mensaje
		gr = create_notUnderstood(AgenteEmpaquetador,None)
	else:
		content = msgdic['content']
		# Averiguamos el tipo de la accion
		accion = gm.value(subject=content, predicate=RDF.type)

		#Llamada dinamica a la accion correspondiente
		if accion in actions:
			gr = actions[accion](gm)
		else:
			gr = create_notUnderstood(AgenteEmpaquetador,None)

	return gr.serialize(format='xml')



def calcularPesoEnvio(envio):

	# Juntamos los pesos para mas rapido acceso
	graph = envios + pesos

	#Miramos el id del envio
	envio_id = graph.value(envio,envios_ns.Id)

	#Obtenemos la colecion del grafo que representa sus productos
	lista = envios_ns[envio_id + '-ListaProductos']

	productos  = Collection(graph,lista)

	#Anadimos las uris de los productos al envio y sumamos el importe total
	peso = 0
	for p in productos: 
		try:
			peso += int(graph.value(p,predicate=productos_ns.Peso))
		except ValueError:
			# Sumamos 0 al peso total
			pass

	return peso

def crearLote(envio):
	peso = calcularPesoEnvio(envio)
	test = lotes_ns["hola"]
	print(test)

def anadirEnvioLote(lote,envio):
	peso = calcularPesoEnvio(envio)

	test = lotes_ns["hola"]
	print(test)
	'''
	node =  lotes.value(subject=lote,predicate=centros_ns.Contiene) or centros_ns[id + '-listaProductos']

	#Afegim el node pare de la coleccio de productes
	g.add((centro,centros_ns.Contiene,node))

	c = Collection(g,node)
	list = []
	for prod in c:
	'''



def registrarEnvio(graph):
	global envios
	envios += graph
	guardarGrafoEnvios(centroLogistico)

def combinarLotes(envio):
	loc = envios.value(envio,envios_ns.Tienedirecciondeentrega)
	cp = envios.value(loc,getNamespace('Direcciones').Codigopostal)

	lotesCandidatos = list(lotes.subjects(predicate=lotes_ns.Ciudad,object=cp))

	lote = None

	if (len(lotesCandidatos) == 0):
		lote = crearLote(envio)
	else:
		lote = random.choice(lotesCandidatos)
		anadirEnvioLote(envio,lote)


def nuevoEnvio(graph):

	envio = graph.subjects(RDF.type,envios_ns.type).next()

	#Obtenemos solo la informacion que nos interesa
	graph = expandirGrafoRec(graph,envio)

	registrarEnvio(graph)
	combinarLotes(envio)

	return create_confirm(AgenteEmpaquetador)

	#Buscar els lots de la ciutat x


def registerActions():
	global actions
	actions[agn.ReceptorNuevoEnvio] = nuevoEnvio

@app.route("/")
def main_page():
	"""
	El hola mundo de los servicios web
	:return:
	"""
	return "soy el agente empaquetador, hola!"



def start_server():
	empaquetador_ns = getNamespace('AgenteEmpaquetador')
	cargarGrafos(centroLogistico)
	register_message(AgenteEmpaquetador,DirectorioAgentes,empaquetador_ns.type)
	registerActions()
	app.run(host=host,port=port,debug=True)


if __name__ == "__main__":
	start_server()

