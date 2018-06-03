import sys
from rdflib import Namespace

agente_prefix = 'http://www.agentes.org/'
tienda_prefix = 'http://www.tienda.org/'
agn = Namespace(agente_prefix)
'''
ns_agentes = {
	'AgenteVendedorExterno':agn.Vendedor,
	'AgenteUsuario':agn.Usuario,
	'AgenteTransportista':agn.Transportista,
	'AgenteServicioPago':agn.Pago,
	'AgenteAdmisor':agn.Admisor,
	'AgenteDevolvedor':agn.Devolvedor,
	'AgenteEnviador':agn.Enviador,
	'AgenteMonetario':agn.Monetario,
	'AgenteReceptor':agn.Receptor,
	'AgenteBuscador':agn.Buscador,
	'AgenteEmpaquetador':agn.Empaquetador,
	'AgenteOpinador':agn.Opinador
}
'''
ns_agentes = {
	'AgenteVendedorExterno':agente_prefix + 'Vendedor',
	'AgenteUsuario':agente_prefix + 'Usuario',
	'AgenteTransportista':agente_prefix + 'Transportista',
	'AgenteServicioPago':agente_prefix + 'Pago',
	'AgenteAdmisor':agente_prefix + 'Admisor',
	'AgenteDevolvedor':agente_prefix + 'Devolvedor',
	'AgenteEnviador':agente_prefix + 'Enviador',
	'AgenteMonetario':agente_prefix + 'Monetario',
	'AgenteReceptor':agente_prefix + 'Receptor',
	'AgenteBuscador':agente_prefix + 'Buscador',
	'AgenteEmpaquetador':agente_prefix + 'Empaquetador',
	'AgenteOpinador':agente_prefix + 'Opinador'
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
	return Namespace(agente_prefix)

def createAction(Agent,actionName):
	return agn[Agent.name + '-' + actionName]

def getNamespace(name):
	if (name in ns_agentes):
		return Namespace(ns_agentes[name] + '#')
	if (name in ns_bases):
		return Namespace(ns_bases[name] + '#')
	raise Exception('Namespace no encontrado')

if __name__ == "__main__":
	pass