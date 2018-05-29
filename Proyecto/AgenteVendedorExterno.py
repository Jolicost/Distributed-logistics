from __future__ import print_function
from multiprocessing import Process
import os.path
#Clase agente
from Util.Agente import Agent
#Renders del flask
from flask import Flask, request, render_template,redirect
from time import sleep
#Funciones para recuperar las direcciones de los agentes
from Util import GestorDirecciones
from Util.ACLMessages import build_message, get_message_properties, send_message
from Util.OntoNamespaces import ACL, DSO
#Utilidades de RDF
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import FOAF, RDF

#Cambiamos la ruta por defecto de los templates para que sea dentro de los ficheros del agente
app = Flask(__name__,template_folder="AgenteVendedorExterno/templates")
agn = None 
AgenteVendedorExterno = None 
AgenteAdmisor = None
host = None
port = None
g = None
graphFile = 'AgenteVendedorExterno/db.turtle'
#Espacio de nombres para los productos y los agentes
agn = Namespace("http://www.agentes.org#")
productos = Namespace("http://www.tienda.org/productos#")

def init_agent():
	dir = GestorDirecciones.getDirAgenteVendedorExterno()
	global host,port,agn,g,AgenteVendedorExterno,AgenteAdmisor
	host = dir['host']
	port = dir['port']
	agn = Namespace("http://www.agentes.org#")
	g = cargarGrafo()
	AgenteVendedorExterno = Agent('AgenteVendedorExterno',agn.AgenteVendedorExterno,dir,port)
	AgenteAdmisor = Agent('AgenteAdmisor',agn.AgenteAdmisor,'cambiarestaurl/comm',None)

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
	res = g.query('''

	SELECT DISTINCT ?q
	WHERE {
		?q ?p ?o
	}
	'''
	)

	for prod in res:
		dic = {}
		s = prod['q']

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
	for triple in producto:
		gcom.add(triple)


	reg_obj = agn[AgenteVendedorExterno.name + "-nuevoProducto"]
	gmess = Graph()
	# Lo metemos en un envoltorio FIPA-ACL y lo enviamos
	msg = build_message(gcom,
		perf=ACL.request,
		sender=AgenteVendedorExterno.uri,
		receiver=AgenteAdmisor.uri,
		content=reg_obj)
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

	guardarGrafo()

def cargarGrafo():
	g = Graph()
	if os.path.isfile(graphFile):
		g.parse(graphFile,format="turtle")
	return g

def guardarGrafo():
	g.serialize(graphFile,format="turtle")	


def tidyup():
	#Instrucciones de parada
	guardarGrafo()

def start_server():
	init_agent()
	app.run()


if __name__ == "__main__":
	start_server()

