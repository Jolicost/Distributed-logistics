# -*- coding: utf-8 -*-
from imports import *

__author__ = 'adrian'

#Cambiamos la ruta por defecto de los templates para que sea dentro de los ficheros del agente
app = Flask(__name__,template_folder="AgenteServicioPago/templates")

argumentos = getArguments(my_port=8011)

host = argumentos['host']
port = argumentos['port']


directorio_host = argumentos['dir_host']
directorio_port = argumentos['dir_port']


#Espacio de nombres para los productos y los agentes
agn = getAgentNamespace()


ServicioPago = Agent('AgenteServicioPago',agenteServicioPago_ns['generic'],formatDir(host,port) + '/comm',None)

#Direccion del directorio que utilizaremos para obtener las direcciones de otros agentes
directorio_host = 'localhost'
directorio_port = 9000
DirectorioAgentes = Agent('DirectorioAgentes',agn.Directory,formatDir(directorio_host,directorio_port) + '/comm',None)

pagos = Graph()
pagos_db = 'Datos/pagos.turtle'

def init_agent():
    register_message(ServicioPago,DirectorioAgentes,agenteServicioPago_ns.type)

#Carga los grafoos rdf de los distintos ficheros
def cargarGrafo():
    global pagos
    pagos = Graph()
    if os.path.isfile(pagos_db):
        pagos.parse(pagos_db,format="turtle")

#Acciones. Este diccionario sera cargado con todos los procedimientos que hay que llamar dinamicamente 
# cuando llega un mensaje
actions = {}

@app.route("/comm")
def comunicacion():
    print("ServicioPago recibe el mensaje")
    global actions
    global ServicioPago
    # Extraemos el mensaje y creamos un grafo con él
    message = request.args['content']
    gm = Graph()
    gm.parse(data=message)
    gm.serialize('test.turtle',format='turtle')
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
    persona = importe = None
    for p, o in graph[ont.Pago]:
        if p == ont.Persona:
            persona = o
        elif p == ont.Importe:
            importe = o

    random = str(randint(0,50))
    tienda = getNamespace('Pagos')
    pagos.add((tienda[persona+importe+random], tienda.Persona, persona))
    pagos.add((tienda[persona+importe+random], tienda.Importe, importe))
    guardarGrafo(pagos, pagos_db)

    return create_confirm(ServicioPago)

def guardarGrafo(g,file):
    g.serialize(file,format="turtle")  

@app.route("/Pagos")
def getPagos():
    global pagos

    idUsuario = request.args['id']
    tienda = getNamespace('Pagos')

    array = []
    #g = Graph()
    for s,p,o in pagos.triples((None, tienda.Persona, Literal(idUsuario))):
        for ss,pp,oo in pagos.triples((s,tienda.Importe,None)):
            #g.add((ss,pp,oo))
            array.append(int(oo))

    #g.serialize('test.turtle',format='turtle')

    return render_template('lista_pagos.html', a = array, u = idUsuario)


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

def getPagos(graph):
    pass

def registerActions():
    global actions
    actions[agn.MonetarioPedirPago] = pedirPago

if __name__ == "__main__":
    registerActions()
    cargarGrafo()
    init_agent()
    # Ponemos en marcha el servidor
    app.run(host=host, port=port, debug=True)
