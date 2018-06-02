import sys
from rdflib import Namespace

agente_prefix = 'http://www.agentes.org#'
tienda_prefix = 'http://www.tienda.org/'
agn = Namespace(agente_prefix)
ns_agentes = {
	'AgenteVendedorExterno':agn.vendedor,
	'AgenteUsuario':agn.usuario,
	'AgenteTransportista':agn.transportista,
	'AgenteServicioPago':agn.pago,
	'AgenteAdmisor':agn.admisor,
	'AgenteDevolvedor':agn.devolvedor,
	'AgenteEnviador':agn.enviador,
	'AgenteMonetario':agn.monetario,
	'AgenteReceptor':agn.receptor,
	'AgenteBuscador':agn.buscador,
	'AgenteEmpaquetador':agn.empaquetador,
	'AgenteOpinador':agn.opinador
}
ns_bases = {
	'Productos':tienda_prefix + 'Productos',
	'Vendedores':tienda_prefix + 'Vendedores',
	'Usuarios':tienda_prefix + 'Usuarios',
	'Pedidos':tienda_prefix + 'Pedidos',
	'Pesos':tienda_prefix + 'Pesos',
	'Envios':tienda_prefix + 'Envios',
	'Lotes':tienda_prefix + 'Lotes',
	'Pagos':tienda_prefix + 'Pagos',
	'Devoluciones':tienda_prefix + 'Devoluciones',
	'Transportistas':tienda_prefix + 'Transportistas',
	'Opiniones':tienda_prefix + 'Opiniones',
	'Ofertas':tienda_prefix + 'Ofertas', #de transporte
	'Peticiones':tienda_prefix + 'Peticiones', #de busqueda
	'Centros':tienda_prefix + 'Centros', #Centros logisticos
}

def getAgentNamespace():
	return agente_prefix

def createAction(Agent,actionName):
	return agn[Agent.name + '-' + actionName]

def getNamespace(name):
	if (name in ns_agentes):
		return ns_agentes[name]
	if (name in ns_bases):
		return Namespace(ns_bases[name] + '#')
	raise Exception('Namespace no encontrado')

if __name__ == "__main__":
	pass