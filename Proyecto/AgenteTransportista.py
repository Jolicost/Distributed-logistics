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
from Util.ModelParser import *
from Util.GraphUtil import *
#Diccionario con los espacios de nombres de la tienda
from Util.Namespaces import getNamespace,getAgentNamespace,createAction
#Utilidades de RDF
from rdflib import Graph, Namespace, Literal,BNode
from rdflib.namespace import FOAF, RDF

app = Flask(__name__,template_folder="AgenteTransportista/templates")

#Direcciones hardcodeadas (propia)
host = 'localhost'
port = 6000
nombre = 'transportista'

directorio_host = 'localhost'
directorio_port = 9000

enviador = getNamespace('AgenteEnviador')
productos = getNamespace('Productos')
transportista_ns = getNamespace('AgenteTransportista')
lotes_ns = getNamespace('Lotes')
envios_ns = getNamespace('Envios')
ofertas_ns = getNamespace('Ofertas')

agn = getAgentNamespace()

g = Graph()

#Objetos agente, no son necesarios en toda regla pero sirven para agilizar comunicaciones
AgenteTransportista = Agent('AgenteTransportista',transportista_ns[nombre],formatDir(host,port) + '/comm',None)
DirectorioAgentes = Agent('DirectorioAgentes',agn.Directory,formatDir(directorio_host,directorio_port) + '/comm',None)
#Cargar el grafo de datos
graphFile = 'AgenteTransportista/' + nombre + '.turtle'

#Acciones. Este diccionario sera cargado con todos los procedimientos que hay que llamar dinamicamente
# cuando llega un mensaje
actions = {}

#Carga el grafo rdf del fichero graphFile
def cargarGrafo():
	global g
	if os.path.isfile(graphFile):
		g.parse(graphFile,format="turtle")
	return g

#cargamos el grafo
g = cargarGrafo()

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
		gr = create_notUnderstood(AgenteTransportista,None)
	else:
		content = msgdic['content']
		# Averiguamos el tipo de la accion
		accion = gm.value(subject=content, predicate=RDF.type)

		#Llamada dinamica a la accion correspondiente
		if accion in actions:
			gr = actions[accion](gm)
		else:
			gr = create_notUnderstood(AgenteTransportista,None)

	return gr.serialize(format='xml')

	return "Envio en curso"


''' Sempre s'ha de ficar el graf de la comunicacio com a parametre en un callback d'accio '''
def peticionOferta(graph):
	print("Recibida peticion de oferta de transporte")

	obj = createAction(AgenteTransportista,'respuestaOferta')
	gcom = Graph()

	# Dummy
	precio = random.randint(1, 10)

	gcom.add((obj,RDF.type,agn.EnviadorOfertaTransporte))
	gcom.add((obj,ofertas_ns.Oferta,Literal(precio)))

	msg = build_message(gcom,
		perf=ACL.inform,
		sender=AgenteTransportista.uri,
		content=obj)

	# Enviamos el mensaje a cualquier agente enviador
	print("Envio respuesta oferta")
	send_message_any(msg,AgenteTransportista,DirectorioAgentes,enviador.type)

def registerActions():
	global actions
	actions[agn.EnviadorPeticionOferta] = peticionOferta

def guardarGrafo():
	g.serialize(graphFile,format="turtle")

@app.route("/")
def main_page():
	"""
	El hola mundo de los servicios web
	:return:
	"""
	return render_template('main.html')



def start_server():
	register_message(AgenteTransportista,DirectorioAgentes,transportista_ns.type)
	registerActions()
	app.run(host=host,port=port,debug=True)

if __name__ == "__main__":
	start_server()
