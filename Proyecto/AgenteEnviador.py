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

app = Flask(__name__,template_folder="AgenteEnviador/templates")

#Direcciones hardcodeadas (propia)
host = 'localhost'
port = 8000
nombre = 'enviador'

directorio_host = 'localhost'
directorio_port = 9000

enviador = getNamespace('AgenteEnviador')
productos = getNamespace('Productos')
pedidos = getNamespace('Pedidos')
lotes_ns = getNamespace('Lotes')
vendedor = getNamespace('AgenteVendedorExterno')

agn = getAgentNamespace()

g = Graph()

#Objetos agente, no son necesarios en toda regla pero sirven para agilizar comunicaciones
AgenteEnviador = Agent('AgenteEnviador',enviador[nombre],formatDir(host,port) + '/comm',None)
DirectorioAgentes = Agent('DirectorioAgentes',agn.Directory,formatDir(directorio_host,directorio_port) + '/comm',None)
#Cargar el grafo de datos
graphFile = 'AgenteEnviador/' + nombre + '.turtle'

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
	# Comprobamos que sea un mensaje FIPA ACL y que la performativa sea correcta
	if not msgdic:
		# Si no es, respondemos que no hemos entendido el mensaje
		gr = create_notUnderstood(AgenteEnviador,None)
	else:
		content = msgdic['content']
		# Averiguamos el tipo de la accion
		accion = gm.value(subject=content, predicate=RDF.type)

		#Llamada dinamica a la accion correspondiente
		if accion in actions:
			gr = actions[accion](gm)
		else:
			gr = create_notUnderstood(AgenteEnviador,None)

	return gr.serialize(format='xml')


@app.route("/test")
def test():
    global lotes_ns
    id = 1234
    gg = Graph()
    for i in range(1,10):
        gg.add((lotes_ns[i],RDF.type,lotes_ns.type))
        gg.add((lotes_ns[i],lotes_ns.Nombre,Literal("name"+str(i))))

    for s in gg.subjects():
        print(gg.triples((s, )))

    print(gg)
    print("TEST PASSED")
    return "Hello agents!"
    #return create_confirm(AgenteEnviador,None)

@app.route("/enviarLote")
def enviarLote(graf):
    #global lotes_ns
    #global g
    #lts = g.subjects(predicate=RDF.type,object=lotes_ns.type)
    #list = []

    #gt = Graph()
    #gt.add((lotes_ns[1], lotes_ns.TestField1, Literal(42)))
    #gt.add((lotes_ns[2], lotes_ns.TestField2, Literal(69)))
    #gettest = gt.triples((lotes_ns[1], None, None))
    #print("-- Result --")
    #for s,p,o in gt:
    #    print (s,p,o)
    #print(gettest)
    #print("-- End result --")
    return "OK"


@app.route("/testMensaje")
def testMensaje():
    obj = createAction(AgenteEnviador,'callbackTest')
    gcom = Graph()

    gcom.add((obj,RDF.type,agn.EnviadorTestCallback))

    msg = build_message(gcom,
        perf=ACL.request,
        sender=AgenteEnviador.uri,
        content=obj)

    # Enviamos el mensaje a cualquier agente admisor
    print("Envio mensaje test")
    send_message_any(msg,AgenteEnviador,DirectorioAgentes,enviador.type)
    return "Envio en curso"


def callbackTest():
    print("Callback working!")

def registerActions():
	global actions
	actions[agn.EnviadorTestCallback] = callbackTest

@app.route("/")
def main_page():
    """
    El hola mundo de los servicios web
    :return:
    """
    return render_template('main.html')


if __name__ == "__main__":
    app.run()


def start_server():
    register_message(AgenteEnviador,DirectorioAgentes,enviador.type)
    registerActions()
    app.run()
