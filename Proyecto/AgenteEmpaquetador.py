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
from Util.Namespaces import getNamespace,getAgentNamespace,createAction
#Utilidades de RDF
from rdflib import Graph, Namespace, Literal,BNode
from rdflib.namespace import FOAF, RDF

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

envios_db = 'Datos/envios.turtle'
lotes_db = 'Datos/lotes.turtle'

#Objetos agente, no son necesarios en toda regla pero sirven para agilizar comunicaciones
AgenteEmpaquetador = Agent('AgenteEmpaquetador',getNamespace('AgenteEmpaquetador')[centroLogistico],formatDir(host,port) + '/comm',None)
DirectorioAgentes = Agent('DirectorioAgentes',agn.Directory,formatDir(directorio_host,directorio_port) + '/comm',None)
#Cargar el grafo de datos

#Acciones. Este diccionario sera cargado con todos los procedimientos que hay que llamar dinamicamente
# cuando llega un mensaje
actions = {}

#Carga el grafo rdf del fichero graphFile
def cargarGrafos():
	global envios,lotes
	if os.path.isfile(envios_db):
		envios.parse(envios_db,format="turtle")
	if os.path.isfile(lotes_db):
		lotes.parse(lotes_db,format="turtle")

def guardarGrafoEnvios():
	envios.serialize(envios_db,format="turtle")

def guardarGrafoLotes():
	lotes.serialize(lotes_db,format="turtle")

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


def nuevoEnvio(graph):
	graph.serialize('test.turtle',format="turtle")
	print("parece que me llega un envio")
	return create_confirm(AgenteEmpaquetador)


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
	cargarGrafos()
	register_message(AgenteEmpaquetador,DirectorioAgentes,empaquetador_ns.type)
	registerActions()
	app.run(host=host,port=port,debug=True)


if __name__ == "__main__":
	start_server()

