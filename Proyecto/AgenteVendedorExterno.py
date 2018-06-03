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

#Diccionario con los espacios de nombres de la tienda
from Datos.Namespaces import getNamespace,getAgentNamespace,createAction
#Utilidades de RDF
from rdflib import Graph, Namespace, Literal,BNode
from rdflib.namespace import FOAF, RDF



host = 'localhost'
port = 8000

admisor_host = 'localhost'
admisor_port = 8001


def cargarGrafo():
	g = Graph()
	if os.path.isfile(graphFile):
		g.parse(graphFile,format="turtle")
	return g



#Cambiamos la ruta por defecto de los templates para que sea dentro de los ficheros del agente
app = Flask(__name__,template_folder="AgenteVendedorExterno/templates")
#Espacios de nombres utilizados
agn = getAgentNamespace()

vendedor = getNamespace('AgenteVendedorExterno')

#Objetos agente
AgenteAdmisor = Agent('AgenteAdmisor',getNamespace('AgenteAdmisor'),formatDir(admisor_host,admisor_port) + '/comm',None)
AgenteVendedorExterno = Agent('AgenteVendedorExterno',getNamespace('AgenteVendedorExterno'),formatDir(host,port) + '/comm',None)
#Cargar el grafo de datos
graphFile = 'AgenteVendedorExterno/db.turtle'
g = cargarGrafo()
#Espacio de nombres para el modelo
productos = getNamespace('Productos')


def init_agent():
	pass

@app.route("/")
def main_page():
	"""
	Pagina principal. No hay acciones extras.
	"""
	return render_template('main.html')


@app.route("/verProductos")
def verProductos():
	"""
	Pagina de productos. Contiene una tabla y poco mas.
	Los productos no tienen estados asociados ya que suponemos que siempre hay stock
	"""
	l = []
	for s in g.subjects(predicate=RDF.type,object=productos.type):
		dic = {}
		dic['resource'] = s
		dic['nom'] = g.value(subject = s,predicate = productos.nombre)
		dic['preu'] = g.value(subject = s,predicate = productos.precio)
		dic['id'] = g.value(subject = s,predicate = productos.id)
		dic['enVenta'] = g.value(subject = s,predicate = productos.enVenta)
		l = l + [dic]

	return render_template('listaProductos.html',list=l)

@app.route("/verPedidos")
def verPedidos():
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
	''' borra el producto de la base de datos local '''
	id = request.args['id']
	g.remove((productos[id],None,None))
	guardarGrafo()
	return redirect("/verProductos")


@app.route("/crearProducto", methods=['GET'])
def crearProducto():
	'''
	enviar datos a la tienda
	'''
	crearProducto(request.args)
	return redirect("/verProductos")

@app.route("/poner_venta", methods=['GET'])
def ponerVenda():
	'''
	enviar datos a la tienda
	'''

	#Id del producto a poner a la venta
	id = request.args['id']

	producto = g.triples((productos[id],None,None))
	gcom = Graph()

	prod = BNode()
	gcom.add((prod,agn.productos,productos[id]))

	for triple in producto:
		gcom.add(triple)


	reg_obj = createAction(AgenteVendedorExterno,'nuevoProducto')
	gcom.add((reg_obj, RDF.type, agn.VendedorNuevoProducto))
	#reg_obj = agn[AgenteVendedorExterno.name + '-nuevoProducto']
	# Lo metemos en un envoltorio FIPA-ACL y lo enviamos
	msg = build_message(gcom,
		perf=ACL.request,
		sender=AgenteVendedorExterno.uri,
		receiver=AgenteAdmisor.uri,
		content=reg_obj)
	print(AgenteAdmisor.address)
	gr = send_message(msg,AgenteAdmisor.address)
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

	nombre = attrs['nombre']
	id = attrs['id']
	precio = attrs['precio']

	#productos[id] crea un recurso con el url del namespace "productos" seguido del identificador
	g.add((productos[id],productos.nombre,Literal(nombre)))
	g.add((productos[id],productos.precio,Literal(precio)))
	g.add((productos[id],productos.id,Literal(id)))
	g.add((productos[id],productos.enVenta,Literal(False)))
	g.add((productos[id],RDF.type,productos.type))


	guardarGrafo()

def guardarGrafo():
	g.serialize(graphFile,format="turtle")	


def tidyup():
	#Instrucciones de parada
	guardarGrafo()

def start_server():
	init_agent()
	app.run(host=host,port=port)


if __name__ == "__main__":
	start_server()

