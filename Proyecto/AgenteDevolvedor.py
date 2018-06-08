# -*- coding: utf-8 -*-
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
import datetime

#Diccionario con los espacios de nombres de la tienda
from Util.Namespaces import getNamespace,getAgentNamespace,createAction
#Utilidades de RDF
from rdflib import Graph, Namespace, Literal,BNode
from rdflib.namespace import FOAF, RDF
from random import randint

__author__ = 'alejandro'

host = 'localhost'
port = 8017

directorio_host = 'localhost'
directorio_port = 9000

monetario_host = 'localhost'
monetario_port = 8002

usuario_host = 'localhost'
usuario_port = 8034

ont = Namespace('Ontologias/root-ontology.owl')
agn = getAgentNamespace()

devolvedor = getNamespace('AgenteDevolvedor')
monetario = getNamespace('AgenteMonetario')
usuario = getNamespace('AgenteUsuario')
#Objetos agente
AgenteDevolvedor = Agent('AgenteDevolvedor',devolvedor['generic'],formatDir(host,port) + '/comm',None)
DirectorioAgentes = Agent('DirectorioAgentes',agn.Directory,formatDir(directorio_host,directorio_port) + '/comm',None)
AgenteMonetario = Agent('AgenteMonetario',monetario['generic'],formatDir(monetario_host,monetario_port) + '/comm',None)
AgenteUsuario = Agent('AgenteUsuario',usuario['generic'],formatDir(usuario_host,usuario_port) + '/comm',None)

devoluciones_ns = getNamespace('Devoluciones')
devoluciones_db = 'Datos/devoluciones.turtle'
devoluciones = Graph()

pedidos_ns = getNamespace('Pedidos')
pedidos_db = 'Datos/pedidos.turtle'
pedidos = Graph()

productos_ns = getNamespace('Productos')

# Flask stuff
app = Flask(__name__)

#Acciones. Este diccionario sera cargado con todos los procedimientos que hay que llamar dinamicamente 
# cuando llega un mensaje
actions = {}

#Carga los grafoos rdf de los distintos ficheros
def cargarGrafos():
    global devoluciones
    global pedidos
    devoluciones = Graph()
    pedidos = Graph()
    if os.path.isfile(devoluciones_db):
        devoluciones.parse(devoluciones_db,format="turtle")
    if os.path.isfile(pedidos_db):
        pedidos.parse(pedidos_db,format="turtle")
    

def guardarGrafo(g,file):
    g.serialize(file,format="turtle")   

def nuevaDevolucion(graph):     #empieza un thread de decidirDevolucion

    ab1 = Process(target=decidirDevolucion, args=(graph))
    ab1.start()

    '''
    global devoluciones
    p = graph.subjects(predicate=RDF.type,object=devoluciones_ns.type)
    for pe in p:
        for a,b,c in graph.triples((pe,None,None)):
            devoluciones.add((a,b,c))
    guardarGrafo(devoluciones,devoluciones_db)'''

    return create_confirm(AgenteDevolvedor,None)

def decidirDevolucion(graph):   #decidir si se acepta o no la devolucion (RazonDevolucion == ("Defectuoso" || "Equivocado" || "NoSatisface"))
    for s,p,o in graph.triples((ont.Devolucion, ont.RazonDevolucion, None)):
        if str(s) == "NoSatisface": #TODO si hace mas de 15 dias desde la recepcion rechazarlo, si no aceptarlo
            elegirEmpresaMensajeria(graph, "NoSatisface")
            #comunicarRespuesta(graph, False, None, None)
        elif str(s) == "Defectuoso":
            elegirEmpresaMensajeria(graph, "Defectuoso")
        elif str(s) == "Equivocado":
            elegirEmpresaMensajeria(graph, "Equivocado")

def elegirEmpresaMensajeria(graph, razon): #elegir la empresa de mensajeria
    int rand = randint(0,4)
    mensajeria = None
    direccion = None
    if rand == 0:
        mensajeria = "Correos"
    elif rand == 1:
        mensajeria = "Seur"
    elif rand == 2:
        mensajeria = "UPS"
    elif rand == 3:
        mensajeria = "ASM"

    if razon == "NoSatisface":
        direccion = "Revision"
    elif razon == "Defectuoso":
        direccion = "Vertedero"
    elif razon == "Equivocado":
        direccion = "Tienda"

    comunicarRespuesta(graph, True, mensajeria, direccion, razon)

def comunicarRespuesta(graph, aceptado, mensajeria, direccion, razon): #si se ha aceptado o no enviar la respuesta al agente de usuario
    persona = None
    importe = None
    producto = None
    for p, o in graph[ont.Devolucion]:
        if p == ont.Persona:
            persona = str(o)
        if p == ont.Producto:
            producto = str(o)

    # hay que mirar la base de datos de productos para ver el importe a devolver
    importe = 1
    pedirReembolso(graph, persona, importe)

    now = datetime.datetime.now()
    fecha = now.day + "-" + now.month + "-" + now.year
    estado = None
    if aceptado:
        estado = "En marcha"
    else:
        estado = "Denegado"

    tienda = getNamespace('Devoluciones')
    devoluciones.add((tienda[persona+producto+fecha], tienda.Persona, persona))
    devoluciones.add((tienda[persona+producto+fecha], tienda.Producto, producto))
    devoluciones.add((tienda[persona+producto+fecha], tienda.Fecha, fecha))
    devoluciones.add((tienda[persona+producto+fecha], tienda.EmpresaMensajeria, mensajeria))
    devoluciones.add((tienda[persona+producto+fecha], tienda.Direccion, direccion))
    devoluciones.add((tienda[persona+producto+fecha], tienda.Razon, razon))
    devoluciones.add((tienda[persona+producto+fecha], tienda.Estado, estado))
    guardarGrafo(devoluciones, devoluciones_db)

    #TODO enviar la respuesta al agente de usuario


def pedirReembolso(graph, persona, importe):      #pedir al agente monetario el reembolso del importe del producto
    global ont
    obj = createAction(AgenteMonetario,'pedirDevolucion')

    gcom = Graph()
    #ontologias
    gcom.add((ont.Pago,ont.Persona,Literal(persona)))
    gcom.add((ont.Pago,ont.Importe,Literal(importe)))
    gcom.add((obj,RDF.type,agn.MonetarioPedirDevolucion))

    msg = build_message(gcom,
        perf=ACL.request,
        sender=AgenteMonetario.uri,
        content=obj)

    # Enviamos el mensaje a cualquier agente monetario
    send_message_any(msg,AgenteMonetario,DirectorioAgentes,monetario.type)

def finalizarDevolucion(graph):
    pass

@app.route("/comm")
def comunicacion():
    global actions
    global AgenteDevolvedor
    # Extraemos el mensaje y creamos un grafo con él
    message = request.args['content']
    gm = Graph()
    gm.parse(data=message)

    msgdic = get_message_properties(gm)
    # Comprobamos que sea un mensaje FIPA ACL y que la performativa sea correcta
    if not msgdic or msgdic['performative'] != ACL.request:
        # Si no es, respondemos que no hemos entendido el mensaje
        gr = create_notUnderstood(AgenteDevolvedor,None)
    else:
        content = msgdic['content']
        # Averiguamos el tipo de la accion
        accion = gm.value(subject=content, predicate=RDF.type)

        #Llamada dinamica a la accion correspondiente
        if accion in actions:
            gr = actions[accion](gm)
        else:
            gr = create_notUnderstood(AgenteDevolvedor,None)

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

def init_agent():
    register_message(AgenteDevolvedor,DirectorioAgentes,devolvedor.type)

def registerActions():
    global actions
    actions[agn.DevolvedorPedirDevolucion] = nuevaDevolucion
    actions[agn.DevolvedorDevolucionRecibida] = finalizarDevolucion #TODO

@app.route("/test1")
def test1():
    global ont
    obj = createAction(AgenteDevolvedor,'nuevaDevolucion')
    gcom = Graph()
    gcom.add((obj,RDF.type,agn.DevolvedorPedirDevolucion))
    
    gcom.add((ont.Devolucion, ont.Pedido, Literal(0)))    #el objeto debera ser el identificador del pedido
    gcom.add((ont.Devolucion, ont.Producto, Literal("Patatas")))    #el objeto debera ser el identificador del producto en un pedido
    gcom.add((ont.Devolucion, ont.Usuario, Literal("adrian")))
    gcom.add((ont.Devolucion, ont.RazonDevolucion, Literal("Defectuoso")))

    msg = build_message(gcom,
        perf=ACL.request,
        sender=AgenteDevolvedor.uri,
        content=obj)
    send_message_any(msg,AgenteDevolvedor,DirectorioAgentes,devolvedor.type)

    return 'Exit'

if __name__ == '__main__':
    # Ponemos en marcha los behaviors
    

    registerActions()

    cargarGrafos()
    init_agent()
    # Ponemos en marcha el servidor
    app.run(host=host, port=port)

    print('The End')
