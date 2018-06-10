# -*- coding: utf-8 -*-
from imports import *
#Generador de juegos de prueba

def crearUsuario(id,tarjeta):
	g = Graph()
	g.add(usuarios_ns[id],RDF.type,usuarios_ns.type)
	g.add(usuarios_ns[id],usuarios_ns.Id,Literal(id))
	g.add(usuarios_ns[id],usuarios_ns.Tarjeta,Literal(tarjeta))
	return g

def crearTransportista(id,nombre):
	g = Graph()
	g.add(transportistas_ns[id],RDF.type,transportistas_ns.type)
	g.add(transportistas_ns[id],transportistas_ns.Id,Literal(id))
	g.add(transportistas_nd[id],transportistas_ns.Nombre,Literal(nombre))

def crearVendedor(id,iban):
	g.add(vendedores_ns[id],RDF.type,vendedores_ns.type)
	g.add(vendedores_ns[id],vendedores_ns.Id,Literal(id))
	g.add(vendedores_ns[id],vendedores_ns.IBAN,Literal(iban))
	return g


def crearCentro(id,dir,cp,pesos):
	pass

def crearProductoPedido(id,estado,fechaEnvio,centro):
	g = Graph()
	g.add((productos_ns[id],RDF.type,productos_ns.type))
	g.add((productos_ns[id],productos_ns.Id,Literal(id)))
	g.add((productos_ns[id],productos_ns.Nombre,Literal(estado)))
	g.add((productos_ns[id],productos_ns.Importe,Literal(fechaEnvio)))
	g.add((productos_ns[id],productos_ns.CentroAsignado,centros_ns[centro]))
	return g

#Productos es una lista de grafos
def crearPedido(id,user_id,prioridad,fecha,importe,direccion,cp,productos):
	g = Graph()
	g.add((pedidos_ns[id],RDF.type,pedidos_ns.type))
	g.add((pedidos_ns[id],pedidos_ns.Id,Literal(id)))
	g.add((pedidos_ns[id],pedidos_ns.Hechopor,usuarios_ns[user_id]))
	g.add((pedidos_ns[id],pedidos_ns.Prioridad,Literal(prioridad)))
	g.add((pedidos_ns[id],pedidos_ns.Fecharealizacion,Literal(fecha)))
	g.add((pedidos_ns[id],pedidos_ns.Importe,Literal(importe)))

	add_localizacion_node(g,pedidos_ns[id],pedidos_ns.Tienedirecciondeentrega,direccion,cp)

	lista = pedidos_ns[id + '-ListaProductos']
	g.add((pedidos_ns[id],pedidos_ns.Contiene,lista))
	c = Collection(g,lista)

	for p in productos:
		node = p.subjects(RDF.type,productos_ns.type).next()
		g+=p
		c.append(node)


def crearProductoExterno(id,nombre,importe,centros,vendedor):
	g = crearProducto(id,nombre,importe,centros)
	g.add((productos_ns[id],productos_ns.Esvendidopor,agenteVendedor_ns[vendedor]))

def crearProducto(id,nombre,importe,centros):
	g = Graph()
	g.add((productos_ns[id],RDF.type,productos_ns.type))
	g.add((productos_ns[id],productos_ns.Id,Literal(id)))
	g.add((productos_ns[id],productos_ns.Nombre,Literal(nombre)))
	g.add((productos_ns[id],productos_ns.Importe,Literal(importe)))
	
	node = productos_ns[id + '-listaCentros']
	g.add((productos_ns[id],productos_ns.CentrosLogisticos,node))
	col = Collection(g,node)

	for centro in centros:
		col.append(centros_ns[centro])

	return g

def crearPeso(prodId,peso):
	pass

def generarCentros():
	pass

def generarProductos():
	g = Graph()
	g+=crearProducto('ProductoPrueba0','Zanahorias',10,['Centro0'])
	g.serialize('test.turtle',format='turtle')






def generarJuegos():
	generarProductos()

if __name__ == '__main__':
	generarJuegos()