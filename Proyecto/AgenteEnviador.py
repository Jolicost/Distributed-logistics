from imports import *

app = Flask(__name__,template_folder="AgenteEnviador/templates")

#Direcciones hardcodeadas (propia)

argumentos = getArguments(my_port=8005,name="enviador")
#Direcciones hardcodeadas (propia)
host = argumentos['host']
port = argumentos['port']

#Nombre del vendedor externo. Servira para generar una URI de recurso
#Aun asi es probable que solo utilitzemos 1 vendedor
nombre = argumentos['name']

directorio_host = argumentos['dir_host']
directorio_port = argumentos['dir_port']

enviador = getNamespace('AgenteEnviador')
transportista_ns = getNamespace('AgenteTransportista')
productos = getNamespace('Productos')
pedidos = getNamespace('Pedidos')
lotes_ns = getNamespace('Lotes')
envios_ns = getNamespace('Envios')
vendedor = getNamespace('AgenteVendedorExterno')
ofertas_ns = getNamespace('Ofertas')

agn = getAgentNamespace()

g = Graph()

#Objetos agente, no son necesarios en toda regla pero sirven para agilizar comunicaciones
AgenteEnviador = Agent('AgenteEnviador',enviador[nombre],formatDir(host,port) + '/comm',None)
AgenteTransportista = Agent('AgenteTransportista',transportista_ns[nombre],formatDir(host,port) + '/comm',None)
DirectorioAgentes = Agent('DirectorioAgentes',agn.Directory,formatDir(directorio_host,directorio_port) + '/comm',None)
#Cargar el grafo de datos
graphFile = 'AgenteEnviador/' + nombre + '.turtle'

#Acciones. Este diccionario sera cargado con todos los procedimientos que hay que llamar dinamicamente
# cuando llega un mensaje
actions = {}

#Carga el grafo rdf del fichero graphFile
def cargarGrafo():
	global g
	if os.path.isfile(graphFile):
		g.parse(graphFile,format="turtle")
	return g

#cargamos el grafo
g = cargarGrafo()

@app.route("/comm")
def comunicacion():
	# Extraemos el mensaje y creamos un grafo con el
	message = request.args['content']
	gm = Graph()
	gm.parse(data=message)

	msgdic = get_message_properties(gm)
	gr = None
	# Comprobamos que sea un mensaje FIPA ACL y que la performativa sea correcta
	if not msgdic:
		# Si no es, respondemos que no hemos entendido el mensaje
		gr = create_notUnderstood(AgenteEnviador,None)
	else:
		content = msgdic['content']
		# Averiguamos el tipo de la accion
		accion = gm.value(subject=content, predicate=RDF.type)

		#Llamada dinamica a la accion correspondiente
		if accion in actions:
			gr = actions[accion](gm)
		else:
			gr = create_notUnderstood(AgenteEnviador,None)

	return gr.serialize(format='xml')

@app.route("/verLotes")
def verLotes():
	lotes = g.subjects(predicate=RDF.type,object=lotes_ns.type)
	print(lotes)
	list = []
	for l in lotes:
		print("Lote:")
		print(l)
		d = lote_a_dict(g,l)
		list += [d]
	return render_template('listaLotes.html',list=list)

def enviarLote(id):
	lote = grafoADict(g, lotes_ns[id])
	lote['envios'] = [] # Temporal, porque si esta vacio peta
	print("Lote:", lote)
	# Marcar pedidos como enviados
	g.set((lotes_ns[id], lotes_ns.Estadodellote, Literal("Enviado")))
	for s in lote['envios']:	# lote['envios'] contiene los ids de los envios
		g.set((s, envios_ns.Estadodelenvio, Literal("Enviado")))
	guardarGrafo()

	# TODO: Enviar factura al usuario

	return "Envio en curso"

@app.route("/pedirOferta")
def pedirOferta():
	id = request.args['id']
	obj = createAction(AgenteEnviador,'peticionOferta')
	gcom = Graph()

	gcom.add((obj,RDF.type,agn.EnviadorPeticionOferta))

	msg = build_message(gcom,
		perf=ACL.inform,
		sender=AgenteEnviador.uri,
		content=obj)

	# Enviamos el mensaje a cualquier agente enviador
	print("Envio mensaje oferta")
	graph = send_message_any(msg,AgenteEnviador,DirectorioAgentes,transportista_ns.type)

	ofertaTransporte(graph, id)
	return redirect("/")

''' Sempre s'ha de ficar el graf de la comunicacio com a parametre en un callback d'accio '''
def callbackTest(graph):
	print("Callback working!")
	return create_confirm(AgenteEnviador)

def ofertaTransporte(graph, id):
	print("Recibida oferta transporte")
	print(graph.serialize(format='turtle'))
	precio = graph.value(subject=ofertas_ns['0'], predicate=ofertas_ns.Oferta)
	print("Precio: ", int(precio))
	enviarLote(id)
	#return create_confirm(AgenteEnviador, AgenteTransportista)

def createFakeLote():
	g.add((lotes_ns['11'],RDF.type,lotes_ns.type))
	g.add((lotes_ns['11'],lotes_ns.Id,Literal(11)))
	g.add((lotes_ns['11'],lotes_ns.Estadodellote,Literal("Idle")))
	g.add((lotes_ns['11'],lotes_ns.Peso,Literal(40)))
	g.add((lotes_ns['11'],lotes_ns.Ciudad,Literal("Bcn")))

	g.add((lotes_ns['15'],RDF.type,lotes_ns.type))
	g.add((lotes_ns['15'],lotes_ns.Id,Literal(15)))
	g.add((lotes_ns['15'],lotes_ns.Estadodellote,Literal("Idle")))
	g.add((lotes_ns['15'],lotes_ns.Peso,Literal(99)))
	g.add((lotes_ns['15'],lotes_ns.Ciudad,Literal("Cancun")))
	print("Created fakes")
	print(g.serialize(format='turtle'))

def registerActions():
	global actions
	actions[agn.EnviadorOfertaTransporte] = ofertaTransporte

def guardarGrafo():
	g.serialize(graphFile,format="turtle")

@app.route("/")
def main_page():
	"""
	El hola mundo de los servicios web
	:return:
	"""
	return render_template('main.html')



def start_server():
	register_message(AgenteEnviador,DirectorioAgentes,enviador.type)
	registerActions()
	createFakeLote()
	app.run(host=host,port=port,debug=True)

if __name__ == "__main__":
	start_server()
