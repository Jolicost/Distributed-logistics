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

#Nombre del vendedor externo. Servira para generar una URI de recurso 
#Aun asi es probable que solo utilitzemos 1 vendedor
nombre = 'vendedorA'


#Direcciones hardcodeadas (propia)
host = 'localhost'
port = 8000

#Direccion del directorio que utilizaremos para obtener las direcciones de otros agentes
directorio_host = 'localhost'
directorio_port = 9000


#Carga el grafo rdf del fichero graphFile
def cargarGrafo():
	g = Graph()
	if os.path.isfile(graphFile):
		g.parse(graphFile,format="turtle")
	return g



#Cambiamos la ruta por defecto de los templates para que sea dentro de los ficheros del agente
app = Flask(__name__,template_folder="AgenteVendedorExterno/templates")
#Espacios de nombres utilizados
#Espacio de los agentes en general
agn = getAgentNamespace()

#Espacio de nombres del vendedor y del admisor (aqui se guardan acciones y demas historias)
vendedor = getNamespace('AgenteVendedorExterno')
admisor = getNamespace('AgenteAdmisor')

#Objetos agente, no son necesarios en toda regla pero sirven para agilizar comunicaciones
AgenteVendedorExterno = Agent('AgenteVendedorExterno',vendedor[nombre],formatDir(host,port) + '/comm',None)
DirectorioAgentes = Agent('DirectorioAgentes',agn.Directory,formatDir(directorio_host,directorio_port) + '/comm',None)
#Cargar el grafo de datos
graphFile = 'AgenteVendedorExterno/' + nombre + '.turtle'
#Espacio de nombres para el modelo de productos
productos = getNamespace('Productos')
pedidos = getNamespace('Pedidos')

#Acciones. Este diccionario sera cargado con todos los procedimientos que hay que llamar dinamicamente 
# cuando llega un mensaje
actions = {}

#cargamos el grafo
g = cargarGrafo()


def init_agent():
	register_message(AgenteVendedorExterno,DirectorioAgentes,vendedor.type)
	pass


def registrarResponsabilidadEnvio(graph):
	pass
	'''
	comunicacion iniciada por el agente receptor
	Indica si el envio corre a cabo de nosotros mismos o de la tienda. 
	Si es a cabo de nosotros nos informaran de los datos de la entrega,
	aunque no haremos mucho con ellos
	'''
	g += graph
	guardarGrafo()

	return create_confirm(AgenteAdmisor,None)

@app.route("/")
def main_page():
	"""
	Pagina principal. Contiene un menu muy simple
	"""
	return render_template('main.html')



@app.route("/comm")
def comunicacion():

	# Extraemos el mensaje y creamos un grafo con él
	message = request.args['content']
	gm = Graph()
	gm.parse(data=message)

	msgdic = get_message_properties(gm)
	# Comprobamos que sea un mensaje FIPA ACL y que la performativa sea correcta
	if not msgdic or msgdic['performative'] != ACL.inform:
		# Si no es, respondemos que no hemos entendido el mensaje
		gr = create_notUnderstood(AgenteAdmisor,None)
	else:
		content = msgdic['content']
		# Averiguamos el tipo de la accion
		accion = gm.value(subject=content, predicate=RDF.type)

		#Llamada dinamica a la accion correspondiente
		if accion in actions:
			gr = actions[accion](gm)
		else:
			gr = create_notUnderstood(AgenteAdmisor,None)

	return gr.serialize(format='xml')


@app.route("/verProductos")
def verProductos():
	"""
	Pagina de productos. Contiene una tabla y poco mas.
	Los productos no tienen estados asociados ya que suponemos que siempre hay stock
	"""
	l = []
	#Todos los productos tienen el predicado "type" a productos.type.
	#De esta forma los obtenemos con mas facilidad y sin consulta sparql
	#La funcoin subjects retorna los sujetos con tal predicado y objeto
	for s in g.subjects(predicate=RDF.type,object=productos.type):
		# Anadimos los atributos que queremos renderizar a la vista
		dic = {}
		dic['resource'] = s
		dic['nom'] = g.value(subject = s,predicate = productos.Nombre)
		dic['preu'] = g.value(subject = s,predicate = productos.Importe)
		dic['id'] = g.value(subject = s,predicate = productos.Id)
		dic['enVenta'] = g.value(subject = s,predicate = productos.enVenta)
		l = l + [dic]

	#Renderizamos la vista
	return render_template('listaProductos.html',list=l)

@app.route("/verPedidos")
def verPedidos():
	#TODO
	"""
	Pagina de pedidos. Se pueden ver que pedidos han sido realizados.
	Tambien se puede ver en que estado se encuentran los pedidos y de quien es la responsabilidad
	Responsabilidad: Nuestra o de la tienda
	Estado: En curso, Enviado
	"""
	l = [{"id":4,"usuario":"joan","estado":"enviado"},{"id":5,"usuario":"manel","estado":"en proceso"}]
	e = [4]
	return render_template('listaPedidos.html',list=l,enviar=e)

@app.route("/enviarPedido")
def enviarPedido():
	""" 
	Representa el envio de un pedido que era responsabilidad del vendedor externo.	
	Se accede a esta accion normalmente a traves de la vista de pedidos 
	"""

@app.route("/anadir")
def nuevoProducto():
	"""
	Mostrar pagina para poner un producto a la venda
	"""
	return render_template('nuevoProducto.html')

@app.route("/borrar")
def borrarProducto():
	''' 
	Borra el producto de la base de datos local
	'''
	id = request.args['id']
	g.remove((productos[id],None,None))
	guardarGrafo()
	return redirect("/verProductos")


@app.route("/crearProducto", methods=['GET'])
def crearProducto():
	'''
	Crea un producto SOLO en local. No envia nada a la tienda.
	'''
	crearProducto(request.args)
	return redirect("/verProductos")

@app.route("/poner_venta", methods=['GET'])
def ponerVenda():
	'''
	Pone un producto en local en venta. Se comunica con la tienda
	'''
	#Pillamos la id del recurso 
	id = request.args['id']

	#Hacemos una subseleccion del grafo con solo el producto a enviar
	producto = g.triples((productos[id],None,None))
	gcom = Graph()

	for triple in producto:
		gcom.add(triple)



	#Esta variable sirve para poca cosa, se podria utilizar cualquier nombre en teoria
	obj = createAction(AgenteVendedorExterno,'nuevoProducto')
	#La variable mas importante es el tipo de accion. Esto se enlaza en esta linea. 
	# Utilizaremos el espacio de nombres agn para referenciar acciones 
	# porque es global a todos los agentes de la tienda
	# Lo que el admisor interpretara sera el agn.VendedorNuevoProducto
	gcom.add((obj, RDF.type, agn.VendedorNuevoProducto))
	# Lo metemos en un envoltorio FIPA-ACL y lo enviamos
	msg = build_message(gcom,
		perf=ACL.request,
		sender=AgenteVendedorExterno.uri,
		content=obj)

	# Enviamos el mensaje a cualquier agente admisor
	send_message_any(msg,AgenteVendedorExterno,DirectorioAgentes,admisor.type)

	#Si todo ha ido correctamente podemos marcar el producto como en venta
	g.set((productos[id],productos.enVenta,Literal(True)))
	return redirect("/")

@app.route("/stop")
def stop():
	"""
	Entrypoint que para el agente

	:return:
	"""
	tidyup()
	shutdown_server()
	return "Parando Servidor"

def crearProducto(attrs):

	#Agarramos los atributos del request http
	nombre = attrs['nombre']
	id = attrs['id']
	precio = attrs['precio']

	#Insertamos todos las relaciones del producto. Notese que tambien tenemos que incorporar 
	#el RDF.type para que sea mas facil consultar sobre los productos mas adelante.
	#Tambien metemos nuestra propia URI de vendedor como Esvendidopor, asi agilizamos el proceso de relacion
	#productos[id] crea un recurso con el url del namespace "productos" seguido del identificador
	g.add((productos[id],productos.Nombre,Literal(nombre)))
	g.add((productos[id],productos.Importe,Literal(precio)))
	g.add((productos[id],productos.Id,Literal(id)))
	g.add((productos[id],productos.enVenta,Literal(False)))
	g.add((productos[id],RDF.type,productos.type))
	g.add((productos[id],productos.Esvendidopor,vendedor[nombre]))


	guardarGrafo()

def guardarGrafo():
	g.serialize(graphFile,format="turtle")	

def registerActions():
	global actions
	actions[agn.ReceptorInformarResponsabilidad] = registrarResponsabilidadEnvio



def tidyup():
	#Instrucciones de parada
	guardarGrafo()

def start_server():
	init_agent()
	app.run(host=host,port=port,debug=True)


if __name__ == "__main__":
	start_server()

