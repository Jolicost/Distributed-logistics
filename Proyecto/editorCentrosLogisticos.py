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
from Util.ACLMessages import build_message, get_message_properties, send_message
from Util.OntoNamespaces import ACL, DSO
from Util.Directorio import *
from Util.GraphUtil import *
from Util.ModelParser import *
from rdflib.collection import Collection

import Util.Namespaces
#Diccionario con los espacios de nombres de la tienda
from Util.Namespaces import getNamespace,getAgentNamespace,createAction
#Utilidades de RDF
from rdflib import Graph, Namespace, Literal,BNode
from rdflib.namespace import FOAF, RDF


#Direcciones hardcodeadas (propia)
host = 'localhost'
port = 8050

#Direccion del directorio que utilizaremos para obtener las direcciones de otros agentes
directorio_host = 'localhost'
directorio_port = 9000

graphFile = 'Datos/centros.turtle'
#grafo de centros
g = Graph()

#Carga el grafo rdf del fichero graphFile
def cargarGrafo():
	g = Graph()
	if os.path.isfile(graphFile):
		g.parse(graphFile,format="turtle")
	return g

def guardarGrafo():
	g.serialize(graphFile,format="turtle")

#Cambiamos la ruta por defecto de los templates para que sea dentro de los ficheros del agente
app = Flask(__name__,template_folder="SharedTemplates")
#Espacios de nombres utilizados
#Espacio de los agentes en general

#cargamos el grafo
g = cargarGrafo()

centros_ns = getNamespace('Centros')

@app.route("/")
def main_page():

	centros = g.subjects(predicate=RDF.type,object=centros_ns.type)

	list = []
	for c in centros:
		print(c)
		list += [centro_a_dict(expandirGrafoRec(g,c),c)]

	return render_template('centros_main.html',list=list)


@app.route("/crearCentro")
def crearCentro():
	return render_template('centros_new.html')

@app.route("/borrarCentro")
def borrarCentro():

	global g
	
	id = request.args['id']

	centro = expandirGrafoRec(g,centros_ns[id])

	g-=centro

	guardarGrafo()

	return redirect("/")

@app.route("/nuevoCentro")
def nuevoCentro():
	global g
	direcciones_ns = getNamespace('Direcciones')

	centro = dict_a_centro(request.args)

	g+=centro
	guardarGrafo()

	return redirect("/")

def tidyup():
	#Instrucciones de parada
	guardarGrafo()

def start_server():
	app.run(host=host,port=port,debug=True)


if __name__ == "__main__":
	start_server()

