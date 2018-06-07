
from Namespaces import *
from rdflib import Graph, Namespace, Literal,BNode
from rdflib.namespace import FOAF, RDF
from rdflib.collection import Collection



def pedido_a_dict(graph,pedido):
	''' devuelve un diccionario con todos los atributos de producto '''
	pedidos_ns = getNamespace('Pedidos')
	direcciones_ns = getNamespace('Direcciones')
	productos_ns = getNamespace('Productos')
	ret = {}
	ret['id'] = graph.value(pedido,pedidos_ns.id)
	ret['user_id'] = graph.value(pedido,pedidos_ns.Hechopor)
	ret['date'] = graph.value(pedido,pedidos_ns.Fecharealizacion)
	ret['prioridad'] = graph.value(pedido,pedidos_ns.Prioridad)
	ret['responsable'] = graph.value(pedido,pedidos_ns.VendedorResponsable) or False

	loc = graph.value(pedido,pedidos_ns.Tienedirecciondeentrega)
	ret['direccion'] = graph.value(loc,direcciones_ns.Direccion)
	ret['cp'] = graph.value(loc,direcciones_ns.Codigopostal)

	prods = []
	container = graph.value(subject=pedido,predicate=pedidos_ns.Contiene)

	c = Collection(graph,container)

	for item in c:
		dict = {}
		dict['id'] = graph.value(subject=item,predicate=productos_ns.Id)
		dict['estado'] = graph.value(subject=item,predicate=productos_ns.EstadoProducto)
		prods += [dict]

	ret['productos'] = prods
	return ret

def dict_a_pedido(dict):

	ret = Graph()

	pedidos_ns = getNamespace('Pedidos')
	direcciones_ns = getNamespace('Direcciones')
	usuarios_ns = getNamespace('AgenteUsuario')
	vendedores_ns = getNamespace('AgenteVendedorExterno')

	id = dict['id']
	user_id = dict['user_id']
	fecha = dict['date']
	prioridad = dict['prioridad']
	direccion = dict['direccion']
	cp = dict['cp']
	vendedor = dict['responsable']
	direccion_id = direccion + cp


	#Nodo padre y su tipo
	ret.add((pedidos_ns[id],RDF.type,pedidos_ns.type))
	ret.add((pedidos_ns[id],pedidos_ns.id,Literal(id)))

	#Anadimos el nodo de la direccion con su tipo y todo
	ret.add((direcciones_ns[direccion_id],RDF.type,direcciones_ns.type))
	ret.add((direcciones_ns[direccion_id],direcciones_ns.Direccion,Literal(direccion)))
	ret.add((direcciones_ns[direccion_id],direcciones_ns.Codigopostal,Literal(cp)))
	#Enlazamos la direccion con el pedido
	ret.add((pedidos_ns[id],pedidos_ns.Tienedirecciondeentrega,direcciones_ns[direccion_id]))

	ret.add((pedidos_ns[id],pedidos_ns.Fecharealizacion,Literal(fecha)))
	ret.add((pedidos_ns[id],pedidos_ns.Prioridad,Literal(prioridad)))
	ret.add((pedidos_ns[id],pedidos_ns.Hechopor,usuarios_ns[user_id]))
	if vendedor: ret.add((pedidos_ns[id],pedidos_ns.VendedorResponsable,vendedores_ns[vendedor]))

	return ret