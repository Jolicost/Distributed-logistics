from imports import * 

app = Flask(__name__,template_folder="AgenteTransportista/templates")

argumentos = getArguments(my_port=8009,name='transportista')

host = argumentos['host']
port = argumentos['port']

nombre = argumentos['name']

directorio_host = argumentos['dir_host']
directorio_port = argumentos['dir_port']


enviador = getNamespace('AgenteEnviador')
productos = getNamespace('Productos')
transportista_ns = getNamespace('AgenteTransportista')
lotes_ns = getNamespace('Lotes')
envios_ns = getNamespace('Envios')
ofertas_ns = getNamespace('Ofertas')

agn = getAgentNamespace()

g = Graph()

#Objetos agente, no son necesarios en toda regla pero sirven para agilizar comunicaciones
AgenteTransportista = Agent('AgenteTransportista',transportista_ns[nombre],formatDir(host,port) + '/comm',None)
DirectorioAgentes = Agent('DirectorioAgentes',agn.Directory,formatDir(directorio_host,directorio_port) + '/comm',None)
#Cargar el grafo de datos
graphFile = 'AgenteTransportista/' + nombre + '.turtle'

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
		gr = create_notUnderstood(AgenteTransportista,None)
	else:
		content = msgdic['content']
		# Averiguamos el tipo de la accion
		accion = gm.value(subject=content, predicate=RDF.type)

		#Llamada dinamica a la accion correspondiente
		if accion in actions:
			gr = actions[accion](gm)
		else:
			gr = create_notUnderstood(AgenteTransportista,None)

	return gr.serialize(format='xml')

	return "Envio en curso"


''' Sempre s'ha de ficar el graf de la comunicacio com a parametre en un callback d'accio '''
def peticionOferta(graph):
	print("Recibida peticion de oferta de transporte")

	obj = createAction(AgenteTransportista,'respuestaOferta')
	gcom = Graph()

	# Dummy
	precio = random.randint(1, 10)

	gcom.add((obj,RDF.type,agn.EnviadorOfertaTransporte))
	gcom.add((obj,ofertas_ns.Oferta,Literal(precio)))

	msg = build_message(gcom,
		perf=ACL.inform,
		sender=AgenteTransportista.uri,
		content=obj)

	return msg

def registerActions():
	global actions
	actions[agn.EnviadorPeticionOferta] = peticionOferta

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
	register_message(AgenteTransportista,DirectorioAgentes,transportista_ns.type)
	registerActions()
	app.run(host=host,port=port,debug=True)

if __name__ == "__main__":
	start_server()
