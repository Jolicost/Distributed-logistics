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
port = 8021


directorio_host = 'localhost'
directorio_port = 9000

name = "Alex"

agn = getAgentNamespace()

usuario = getNamespace('AgenteUsuario')
opinador = getNamespace('AgenteOpinador')
#Objetos agente
AgenteUsuario = Agent('AgenteUsuario',usuario['generic'],formatDir(host,port) + '/comm',None)
DirectorioAgentes = Agent('DirectorioAgentes',agn.Directory,formatDir(directorio_host,directorio_port) + '/comm',None)

opiniones_ns = getNamespace('Opiniones')

recomendaciones_db = 'Datos/recomendaciones.turtle'

productos_ns = getNamespace('Productos')

productos_db = 'Datos/productos.turtle'
productos = Graph()


cola1 = Queue()


#Acciones. Este diccionario sera cargado con todos los procedimientos que hay que llamar dinamicamente 
# cuando llega un mensaje
actions = {}



app = Flask(__name__,template_folder="AgenteUsuario/templates")


def cargarGrafos():
    global productos
    opiniones = Graph()
    if os.path.isfile(opiniones_db):
        opiniones.parse(opiniones_db,format="turtle")
    elif os.path.isfile(productos_db):
        productos.parse(productos_db,format="turtle")
    

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

@app.route("/crearOpinion", methods=['GET'])
def darOpinion():
    crearOpinion(request.args)
    return redirect("/")

def crearOpinion(attrs):
    puntuacion = attrs['puntuacion']
    descripcion = attrs['descripcion']
    g = Graph()
    g.add((opiniones_ns[1],opiniones_ns.puntuacion,Literal(puntuacion)))
    g.add((opiniones_ns[1],opiniones_ns.descripcion,Literal(descripcion)))
    obj = createAction(AgenteUsuario,'darOpinion')

    g.add((obj, RDF.type, agn.DarOpinion))
    
    msg = build_message(g,
        perf=ACL.request,
        sender=AgenteUsuario.uri,
        content=obj)

    # Enviamos el mensaje a cualquier agente admisor
    send_message_all(msg,AgenteUsuario,DirectorioAgentes,opinador.type)


@app.route("/opinar")
def nuevaOpinion():
    """
    Mostrar pagina para poner un producto a la venda
    """
    return render_template('darOpinion.html')

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
    resultado = ["peras","manzanas","zanahorias"]

    return render_template(
        'resultadoBusqueda.html',
        criterio=request.args['criterio'],
        values=resultado)

def rebreRecomanacions(graph):
    guardarGrafo(graph, recomendaciones_db)
    return create_confirm(AgenteUsuario,None)

def registerActions():
    global actions
    actions[agn.RecomendarProductos] = rebreRecomanacions

def init_agent():
    register_message(AgenteUsuario,DirectorioAgentes,usuario.type)

def start_server():
    init_agent()
    registerActions()
    app.run(host=host,port=port,debug=True)


if __name__ == "__main__":
    start_server()