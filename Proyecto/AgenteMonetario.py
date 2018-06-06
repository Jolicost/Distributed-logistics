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
from Util.Directorio import *

#Diccionario con los espacios de nombres de la tienda
from Util.Namespaces import getNamespace,getAgentNamespace,createAction
#Utilidades de RDF
from rdflib import Graph, Namespace, Literal,BNode
from rdflib.namespace import FOAF, RDF

#Cambiamos la ruta por defecto de los templates para que sea dentro de los ficheros del agente
app = Flask(__name__,template_folder="AgenteVendedorExterno/templates")
host = 'localhost'
port = 8002
pago_host = 'localhost'
pago_port = 8003
#Espacio de nombres para los productos y los agentes
agn = getAgentNamespace()
monetario = getNamespace('AgenteMonetario')
pago = getNamespace('AgenteServicioPago')
AgenteMonetario = Agent('AgenteMonetario',monetario['generic'],formatDir(host,port) + '/comm',None)
ServicioPago = Agent('AgenteServicioPago',pago['generic'],formatDir(pago_host,pago_port) + '/comm',None)

actions = {}

#Direccion del directorio que utilizaremos para obtener las direcciones de otros agentes
directorio_host = 'localhost'
directorio_port = 9000
DirectorioAgentes = Agent('DirectorioAgentes',agn.Directory,formatDir(directorio_host,directorio_port) + '/comm',None)

def init_agent():
    register_message(AgenteMonetario,DirectorioAgentes,monetario.type)

@app.route("/comm")
def comunicacion():
    global actions
    global ServicioPago
    global AgenteMonetario
    # Extraemos el mensaje y creamos un grafo con él
    message = request.args['content']
    gm = Graph()
    gm.parse(data=message)

    msgdic = get_message_properties(gm)

    print(message)
    # Comprobamos que sea un mensaje FIPA ACL y que la performativa sea correcta
    if not msgdic or msgdic['performative'] != ACL.request:
        # Si no es, respondemos que no hemos entendido el mensaje
        gr = create_notUnderstood(AgenteMonetario,None)
    else:
        content = msgdic['content']
        # Averiguamos el tipo de la accion
        accion = gm.value(subject=content, predicate=RDF.type)

        #Llamada dinamica a la accion correspondiente
        if accion in actions:
            gr = actions[accion](gm)
        else:
            gr = create_notUnderstood(AgenteMonetario,None)

    return gr.serialize(format='xml')

def pedirPago(graph):

    obj = createAction(ServicioPago,'pedirPago')

    gcom = graph
    gcom.remove((None, RDF.type, None))
    gcom.add((obj,RDF.type,agn.MonetarioPedirPago))

    msg = build_message(gcom,
        perf=ACL.request,
        sender=AgenteMonetario.uri,
        content=obj)

    # Enviamos el mensaje a cualquier agente admisor
    send_message_any(msg,AgenteMonetario,DirectorioAgentes,pago.type)

    return create_confirm(AgenteMonetario,None)

@app.route("/test")
def test():
    obj = createAction(ServicioPago,'pedirPago')

    gcom = Graph()
    #ontologias
    ont = Namespace('Ontologias/root-ontology.owl')
    pago = ont.Pago
    gcom.add((pago,ont.Persona,Literal('megadri')))
    gcom.add((pago,ont.Importe,Literal(20)))

    msg = build_message(gcom,
        perf=ACL.request,
        sender=AgenteMonetario.uri,
        content=obj)

    # Enviamos el mensaje a cualquier agente admisor
    print("Agente monetario envia mensaje a servicio pago")
    send_message_any(msg,AgenteMonetario,DirectorioAgentes,pago.type)

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
    createAction(AgenteMonetario, 'pedirPago')

if __name__ == "__main__":
    registerActions()
    init_agent()
    # Ponemos en marcha el servidor
    app.run(host=host, port=port, debug=True)
