from __future__ import print_function
from multiprocessing import Process
#Clase agente
from Util.Agente import Agent
#Renders del flask
from flask import Flask, request, render_template
from time import sleep
#Funciones para recuperar las direcciones de los agentes
from Util import GestorDirecciones
#Utilidades de RDF
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import FOAF, RDF

#Cambiamos la ruta por defecto de los templates para que sea dentro de los ficheros del agente
app = Flask(__name__,template_folder="AgenteVendedorExterno/templates")
agn = None 
AgenteVendedorExterno = None 
host = None
port = None
AgenteVendedorExterno = None

def init_agent():
	dir = GestorDirecciones.getDirAgenteVendedorExterno()
	host = dir['host']
	port = dir['port']
	agn = Namespace("http://www.agentes.org#")
	AgenteVendedorExterno = Agent('AgenteVendedorExterno',agn.AgenteVendedorExterno,dir,port)


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
	l = [{"id":5,"preu":4,"marca":"nike"},{"id":6,"preu":5,"marca":"adidas"}]
	v = [5]
	return render_template('listaProductos.html',list=l,venta=v)

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
	return render_template('render_text.html',text=str(request.args['id']))


@app.route("/poner_venda", methods=['GET'])
def poner_venda():
	'''
	enviar datos a la tienda
	'''
	return render_template('render_text.html',text=str(request.args['id']))

def start_server():
	init_agent()
	app.run()


if __name__ == "__main__":
	start_server()

