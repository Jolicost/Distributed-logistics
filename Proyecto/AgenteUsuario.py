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

__author__ = 'alejandro'

host = 'localhost'
port = 8034


directorio_host = 'localhost'
directorio_port = 9000


ont = Namespace('Ontologias/root-ontology.owl')

name = "Alex"
id_user = 1

agn = getAgentNamespace()

usuario = getNamespace('AgenteUsuario')
opinador = getNamespace('AgenteOpinador')
buscador = getNamespace('AgenteBuscador')
devolvedor = getNamespace('AgenteDevolvedor')
#Objetos agente
AgenteUsuario = Agent('AgenteUsuario',usuario['generic'],formatDir(host,port) + '/comm',None)
DirectorioAgentes = Agent('DirectorioAgentes',agn.Directory,formatDir(directorio_host,directorio_port) + '/comm',None)

productosOpinar_db = 'Datos/productos_a_opinar.turtle'

recomendaciones_db = 'Datos/recomendaciones.turtle'

productos_ns = getNamespace('Productos')

pedidos_ns = getNamespace('Pedidos')

productos_db = 'Datos/productos.turtle'
productos = Graph()

devoluciones_ns = getNamespace('Devoluciones')

opiniones_ns = getNamespace('Opiniones')
productos_a_opinar = Graph()

peticiones_ns = getNamespace('Peticiones')

cola1 = Queue()


#Acciones. Este diccionario sera cargado con todos los procedimientos que hay que llamar dinamicamente 
# cuando llega un mensaje
actions = {}



app = Flask(__name__,template_folder="AgenteUsuario/templates")


def cargarGrafos():
    global productos
    opiniones = Graph()
    if os.path.isfile(productosOpinar_db):
        productos_a_opinar.parse(productosOpinar_db,format="turtle")

    

def guardarGrafo(g,file):
    g.serialize(file,format="turtle")   

@app.route("/")
def main_page():
    """
    El hola mundo de los servicios web
    :return:
    """
    return render_template('main.html')

@app.route("/recomendaciones")
def verRecomendaciones():
    g = Graph()
    if os.path.isfile(recomendaciones_db):
        g.parse(recomendaciones_db,format="turtle")
    l = []
    #Todos los productos tienen el predicado "type" a productos.type.
    #De esta forma los obtenemos con mas facilidad y sin consulta sparql
    #La funcoin subjects retorna los sujetos con tal predicado y objeto
    for s in g.subjects(predicate=RDF.type,object=productos_ns.type):
        # Anadimos los atributos que queremos renderizar a la vista
        dic = {}
        dic['resource'] = s
        dic['nom'] = g.value(subject = s,predicate = productos_ns.Nombre)
        dic['preu'] = g.value(subject = s,predicate = productos_ns.Importe)
        dic['id'] = g.value(subject = s,predicate = productos_ns.Id)
        l = l + [dic]

    #Renderizamos la vista
    return render_template('recomendaciones.html',list=l)

@app.route("/opinar")
def verProductosaOpinar():
    g = Graph()
    if os.path.isfile(productosOpinar_db):
        g.parse(productosOpinar_db,format="turtle")
    l = []
    #Todos los productos tienen el predicado "type" a productos.type.
    #De esta forma los obtenemos con mas facilidad y sin consulta sparql
    #La funcoin subjects retorna los sujetos con tal predicado y objeto
    for s in g.subjects(predicate=RDF.type,object=productos_ns.type):
        # Anadimos los atributos que queremos renderizar a la vista
        dic = {}
        dic['nom'] = g.value(subject = s,predicate = productos_ns.Nombre)
        dic['id'] = g.value(subject = s,predicate = productos_ns.Id)
        l = l + [dic]

    #Renderizamos la vista
    return render_template('listaProductosaOpinar.html',list=l)

@app.route("/productosaOpinar/<id>/opinar", methods=['GET'])
def darOpinion(id):
    return render_template('darOpinion.html',id=id)

@app.route("/devolver")
def verProductosaDevolver():
    g = Graph()
    if os.path.isfile(productos_db):
        g.parse(productos_db,format="turtle")
    l = []
    #Todos los productos tienen el predicado "type" a productos.type.
    #De esta forma los obtenemos con mas facilidad y sin consulta sparql
    #La funcoin subjects retorna los sujetos con tal predicado y objeto
    for s in g.subjects(predicate=RDF.type,object=productos_ns.type):
        # Anadimos los atributos que queremos renderizar a la vista
        dic = {}
        dic['nom'] = g.value(subject = s,predicate = productos_ns.Nombre)
        dic['id'] = g.value(subject = s,predicate = productos_ns.Id)
        l = l + [dic]

    #Renderizamos la vista
    return render_template('listaProductosDevolver.html',list=l)

@app.route("/productosDevolver/<id>/devolver", methods=['GET'])
def crearDevolucion(id):
    return render_template('crearPeticionDevolucion.html',id=id)


@app.route("/productosDevolver/<id>/crearDevolucion", methods=['GET'])        
def crearPeticionDevolucion(id):
    razon = request.args['razon']
    g = Graph()
    g.add((devoluciones_ns[str(id_user)+str(id)], productos_ns.Id, Literal(id)))
    g.add((devoluciones_ns[str(id_user)+str(id)], pedidos_ns.Id, Literal("2")))
    g.add((devoluciones_ns[str(id_user)+str(id)], usuario.Id, Literal(name)))
    g.add((devoluciones_ns[str(id_user)+str(id)], RDF.type, devoluciones_ns.type))
    obj = createAction(AgenteUsuario,'crearDevolucion')

    g.add((obj, RDF.type, agn.DevolvedorPedirOpinion))
    msg = build_message(g,
        perf=ACL.request,
        sender=AgenteUsuario.uri,
        content=obj)

    # Enviamos el mensaje a cualquier agente admisor
    send_message_any(msg,AgenteUsuario,DirectorioAgentes,devolvedor.type)
    """
    for p in g.subjects(predicate=productos_ns.Id, object=Literal(id)):
        for a,b,c in graph.triples((p,None,None)):
            productos_a_opinar.remove(a,b,c)
    guardarGrafo(productos_a_opinar, productosOpinar_db)
    """
    return redirect("/devolver")

@app.route("/productosaOpinar/<id>/crearOpinion", methods=['GET'])
def crearOpinion(id):
    puntuacion = request.args['puntuacion']
    descripcion = request.args['descripcion']
    g = Graph()
    g.add((opiniones_ns[str(id_user)+str(id)], devoluciones_ns.producto, Literal(id)))
    g.add((opiniones_ns[str(id_user)+str(id)], opiniones_ns.puntuacion, Literal(puntuacion)))
    g.add((opiniones_ns[str(id_user)+str(id)], opiniones_ns.descripcion, Literal(descripcion)))
    g.add((opiniones_ns[str(id_user)+str(id)], RDF.type, opiniones_ns.type))
    obj = createAction(AgenteUsuario,'darOpinion')

    g.add((obj, RDF.type, agn.DarOpinion))
    msg = build_message(g,
        perf=ACL.request,
        sender=AgenteUsuario.uri,
        content=obj)

    # Enviamos el mensaje a cualquier agente admisor
    send_message_any(msg,AgenteUsuario,DirectorioAgentes,opinador.type)
    """
    for p in g.subjects(predicate=productos_ns.Id, object=Literal(id)):
        for a,b,c in graph.triples((p,None,None)):
            productos_a_opinar.remove(a,b,c)
    guardarGrafo(productos_a_opinar, productosOpinar_db)
    """
    return redirect("/opinar")

@app.route("/buscar")
def pag():
    """
    Entrada que sirve una pagina de web que cuenta hasta 10
    :return:
    """
    return render_template('buscarProductos.html')

@app.route("/comm")
def comunicacion():
    # Extraemos el mensaje y creamos un grafo con el
    message = request.args['content']
    gm = Graph()
    gm.parse(data=message)

    msgdic = get_message_properties(gm)
    # Comprobamos que sea un mensaje FIPA ACL y que la performativa sea correcta
    if not msgdic or msgdic['performative'] != ACL.request:
        # Si no es, respondemos que no hemos entendido el mensaje
        gr = create_notUnderstood(AgenteUsuario,None)
    else:
        content = msgdic['content']
        # Averiguamos el tipo de la accion
        accion = gm.value(subject=content, predicate=RDF.type)

        #Llamada dinamica a la accion correspondiente
        if accion in actions:
            gr = actions[accion](gm)
        else:
            gr = create_notUnderstood(AgenteUsuario,None)

    return gr.serialize(format='xml')


@app.route("/buscarProductos", methods=['GET','POST'])
def buscarProductos():
    criterio = request.args['criterio']
    g = Graph()
    g.add((peticiones_ns[str(id_user)+criterio], peticiones_ns.Busqueda, Literal(criterio)))
    g.add((peticiones_ns[str(id_user)+criterio], peticiones_ns.Id, Literal(str(id_user)+criterio)))
    g.add((peticiones_ns[str(id_user)+criterio], peticiones_ns.User, Literal(AgenteUsuario.uri)))
    g.add((peticiones_ns[str(id_user)+criterio], RDF.type, peticiones_ns.type))
    obj = createAction(AgenteUsuario,'peticionBusqueda')

    g.add((obj, RDF.type, agn.peticionBusqueda))
    msg = build_message(g,
        perf=ACL.request,
        sender=AgenteUsuario.uri,
        content=obj)

    # Enviamos el mensaje a cualquier agente admisor
    res = send_message_any(msg,AgenteUsuario,DirectorioAgentes,buscador.type)
    l = []
    #Todos los productos tienen el predicado "type" a productos.type.
    #De esta forma los obtenemos con mas facilidad y sin consulta sparql
    #La funcoin subjects retorna los sujetos con tal predicado y objeto
    for s in res.subjects(predicate=RDF.type,object=productos_ns.type):
        # Anadimos los atributos que queremos renderizar a la vista
        dic = {}
        dic['nom'] = res.value(subject = s,predicate = productos_ns.Nombre)
        dic['id'] = res.value(subject = s,predicate = productos_ns.Id)
        dic['import'] = res.value(subject = s,predicate = productos_ns.Importe)
        l = l + [dic]

    #Renderizamos la vista
    return render_template('resultadoBusqueda.html',criterio=criterio, list=l)

def rebreRecomanacions(graph):
    guardarGrafo(graph, recomendaciones_db)
    return create_confirm(AgenteUsuario,None)

def recibirProductosaOpinar(graph):
    productos_a_opinar = graph
    guardarGrafo(graph,productosOpinar_db)
    return create_confirm(AgenteUsuario,None)
"""
def resultadoDevolucion(graph):
    l = []
    #Todos los productos tienen el predicado "type" a productos.type.
    #De esta forma los obtenemos con mas facilidad y sin consulta sparql
    #La funcoin subjects retorna los sujetos con tal predicado y objeto
    for s in res.subjects(predicate=RDF.type,object=devoluciones_ns.type):
        # Anadimos los atributos que queremos renderizar a la vista
        dic = {}
        dic['nom'] = res.value(subject = s,predicate = ont.Producto)
        dic['razon'] = res.value(subject = s,predicate = ont.Razon)
        dic['estado'] = res.value(subject = s,predicate = ont.Estado)
        l = l + [dic]
    return render_template('devoluciones.html',list=l)
"""
def registerActions():
    global actions
    actions[agn.RecomendarProductos] = rebreRecomanacions
    actions[agn.PedirOpiniones] = recibirProductosaOpinar
    #actions[agn.resultadoBusqueda] = mostrarResultadoBusqueda

def init_agent():
    register_message(AgenteUsuario,DirectorioAgentes,usuario.type)

def start_server():
    init_agent()
    registerActions()
    cargarGrafos()
    app.run(host=host,port=port,debug=True)


if __name__ == "__main__":
    start_server()