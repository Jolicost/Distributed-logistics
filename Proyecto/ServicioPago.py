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
from Util.ACLMessages import build_message, get_message_properties, send_message, create_confirm
from Util.OntoNamespaces import ACL, DSO

#Diccionario con los espacios de nombres de la tienda
from Datos.Namespaces import getNamespace,getAgentNamespace,createAction
#Utilidades de RDF
from rdflib import Graph, Namespace, Literal,BNode
from rdflib.namespace import FOAF, RDF

#Cambiamos la ruta por defecto de los templates para que sea dentro de los ficheros del agente
app = Flask(__name__,template_folder="ServicioPago/templates")
host = 'localhost'
port = 8003
monetario_host = 'localhost'
monetario_port = 8002
#Espacio de nombres para los productos y los agentes
agn = getAgentNamespace()
pago = getNamespace('AgenteServicioPago')
monetario = getNamespace('AgenteMonetario')
ServicioPago = Agent('AgenteServicioPago',pago['generic'],formatDir(host,port) + '/comm',None)
AgenteMonetario = Agent('AgenteMonetario',monetario['generic'],formatDir(monetario_host,monetario_port) + '/comm',None)

#Direccion del directorio que utilizaremos para obtener las direcciones de otros agentes
directorio_host = 'localhost'
directorio_port = 9000
DirectorioAgentes = Agent('DirectorioAgentes',agn.Directory,formatDir(directorio_host,directorio_port) + '/comm',None)

pagos = Graph()
pagos_db = 'Datos/pagos.turtle'

def init_agent():
    register_message(ServicioPago,DirectorioAgentes,pago.type)

#Carga los grafoos rdf de los distintos ficheros
def cargarGrafo():
    global pagos
    pagos = Graph()
    if os.path.isfile(pagos_db):
        productos.parse(pagos_db,format="turtle")

#Acciones. Este diccionario sera cargado con todos los procedimientos que hay que llamar dinamicamente 
# cuando llega un mensaje
actions = {}

@app.route("/comm")
def comunicacion():
    global actions
    global ServicioPago
    # Extraemos el mensaje y creamos un grafo con él
    message = request.args['content']
    gm = Graph()
    gm.parse(data=message)

    msgdic = get_message_properties(gm)

    print(message)
    # Comprobamos que sea un mensaje FIPA ACL y que la performativa sea correcta
    if not msgdic or msgdic['performative'] != ACL.request:
        # Si no es, respondemos que no hemos entendido el mensaje
        gr = create_notUnderstood(ServicioPago,None)
    else:
        content = msgdic['content']
        # Averiguamos el tipo de la accion
        accion = gm.value(subject=content, predicate=RDF.type)

        #Llamada dinamica a la accion correspondiente
        if accion in actions:
            gr = actions[accion](gm)
        else:
            gr = create_notUnderstood(ServicioPago,None)

    return gr.serialize(format='xml')

def pedirPago(graph):
    global pagos
    global pagos_db

    #ontologias
    ont = Namespace('Ontologias/root-ontology.owl')
    pago = ont.Pago
    persona = importe = None
    for p, o in g[pago]
        if p == ont.Persona:
            persona = o
        elif p == ont.Importe:
            importe = o

    pagos.add((persona, ont.Pago, importe))
    guardarGrafo(pagos, pagos_db)

    return create_confirm(ServicioPago,AgenteMonetario)

def guardarGrafo(g,file):
    g.serialize(file,format="turtle")  

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

def registerActions():
    global actions
    actions[agn.MonetarioPedirPago] = pedirPago

if __name__ == "__main__":
    registerActions()
    cargarGrafo()
    init_agent()
    # Ponemos en marcha el servidor
    app.run(host=host, port=port)
