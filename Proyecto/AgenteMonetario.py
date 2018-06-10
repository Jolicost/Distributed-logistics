# -*- coding: utf-8 -*-
from imports import * 

__author__ = 'adrian'


argumentos = getArguments(my_port=8006)

host = argumentos['host']
port = argumentos['port']

directorio_host = argumentos['dir_host']
directorio_port = argumentos['dir_port']

#Cambiamos la ruta por defecto de los templates para que sea dentro de los ficheros del agente
app = Flask(__name__,template_folder="AgenteVendedorExterno/templates")

#Espacio de nombres para los productos y los agentes
agn = getAgentNamespace()

AgenteMonetario = Agent('AgenteMonetario',agenteMonetario_ns['generic'],formatDir(host,port) + '/comm',None)

actions = {}

#Direccion del directorio que utilizaremos para obtener las direcciones de otros agentes
directorio_host = 'localhost'
directorio_port = 9000
DirectorioAgentes = Agent('DirectorioAgentes',agn.Directory,formatDir(directorio_host,directorio_port) + '/comm',None)

def init_agent():
    register_message(AgenteMonetario,DirectorioAgentes,agenteMonetario_ns.type)

@app.route("/comm")
def comunicacion():
    global actions
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

def pedirPagoPedido(graph):

    obj = createAction(ServicioPago,'pedirPago')
    
    gcom = graph
    gcom.remove((None, RDF.type, None))
    gcom.add((obj,RDF.type,agn.MonetarioPedirPago))

    msg = build_message(gcom,
        perf=ACL.request,
        sender=AgenteMonetario.uri,
        content=obj)

    # Enviamos el mensaje a cualquier servicio de pago
    send_message_any(msg,AgenteMonetario,DirectorioAgentes,agenteServicioPago_ns.type)

    return create_confirm(AgenteMonetario,None)

def pedirPagoTiendaExterna(graph):

    obj = createAction(ServicioPago,'pedirPago')

    gcom = graph
    gcom.remove((None, RDF.type, None))
    gcom.add((obj,RDF.type,agn.MonetarioPedirPago))

    msg = build_message(gcom,
        perf=ACL.request,
        sender=AgenteMonetario.uri,
        content=obj)

    # Enviamos el mensaje a cualquier agente admisor
    send_message_any(msg,AgenteMonetario,DirectorioAgentes,agenteServicioPago_ns.type)

    return create_confirm(AgenteMonetario,None)

def pedirDevolucion(graph):

    obj = createAction(ServicioPago,'pedirPago')
    #ontologias
    ont = Namespace('Ontologias/root-ontology.owl')
    gcom = graph
    gcom.remove((None, RDF.type, None))
    gcom.add((obj,RDF.type,agn.MonetarioPedirPago))
    #gcom.serialize('test2.turtle',format='turtle')

    for s,p,o in gcom.triples((ont.Pago, ont.Importe, None)):
        n = int(o)
        n *= -1
        gcom.set((ont.Pago, ont.Importe, Literal(n)))
    #gcom.serialize('test3.turtle',format='turtle')

    msg = build_message(gcom,
        perf=ACL.request,
        sender=AgenteMonetario.uri,
        content=obj)
    # Enviamos el mensaje a cualquier agente admisor
    send_message_any(msg,AgenteMonetario,DirectorioAgentes,agenteServicioPago_ns.type)

    return create_confirm(AgenteMonetario,None)

@app.route("/test1")
def test1():
    obj = createAction(AgenteMonetario,'pedirPagoPedido')


    gcom = Graph()
    #ontologias
    ont = Namespace('Ontologias/root-ontology.owl')
    gcom.add((ont.Pago,ont.Persona,Literal('adri')))
    gcom.add((ont.Pago,ont.Importe,Literal(20)))
    gcom.add((obj,RDF.type,agn.MonetarioPedirPagoPedido))

    msg = build_message(gcom,
        perf=ACL.request,
        sender=AgenteMonetario.uri,
        content=obj)

    # Enviamos el mensaje a cualquier agente admisor
    print("Agente monetario envia mensaje a servicio pago")
    send_message_any(msg,AgenteMonetario,DirectorioAgentes,agenteMonetario_ns.type)
    return 'Exit'

@app.route("/test2")
def test2():
    obj = createAction(AgenteMonetario,'pedirPagoTiendaExterna')


    gcom = Graph()
    #ontologias
    ont = Namespace('Ontologias/root-ontology.owl')
    gcom.add((ont.Pago,ont.Persona,Literal('alex')))
    gcom.add((ont.Pago,ont.Importe,Literal(30)))
    gcom.add((obj,RDF.type,agn.MonetarioPedirPagoTiendaExterna))

    msg = build_message(gcom,
        perf=ACL.request,
        sender=AgenteMonetario.uri,
        content=obj)

    # Enviamos el mensaje a cualquier agente admisor
    print("Agente monetario envia mensaje a servicio pago")
    send_message_any(msg,AgenteMonetario,DirectorioAgentes,agenteMonetario_ns.type)
    return 'Exit'

@app.route("/test3")
def test3():
    obj = createAction(AgenteMonetario,'pedirDevolucion')


    gcom = Graph()
    #ontologias
    ont = Namespace('Ontologias/root-ontology.owl')
    gcom.add((ont.Pago,ont.Persona,Literal('alex')))
    gcom.add((ont.Pago,ont.Importe,Literal(60)))
    gcom.add((obj,RDF.type,agn.MonetarioPedirDevolucion))

    msg = build_message(gcom,
        perf=ACL.request,
        sender=AgenteMonetario.uri,
        content=obj)

    # Enviamos el mensaje a cualquier agente admisor
    print("Agente monetario envia mensaje a servicio pago")
    send_message_any(msg,AgenteMonetario,DirectorioAgentes,agenteMonetario_ns.type)
    return 'Exit'

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
    actions[agn.MonetarioPedirPagoPedido] = pedirPagoPedido
    actions[agn.MonetarioPedirPagoTiendaExterna] = pedirPagoTiendaExterna
    actions[agn.MonetarioPedirDevolucion] = pedirDevolucion

if __name__ == "__main__":
    registerActions()
    init_agent()
    # Ponemos en marcha el servidor
    app.run(host=host, port=port, debug=True)
