''' Utilidades del objeto grafo de rdt '''
from rdflib import Graph

''' 
recorrido DFS del grafo a partir de un node en especifico. 
Util para encontrar todos los atributos de un cierto recurso en recursivo 
'''
def expandirGrafoRec(grafo,nodo):
	g = Graph()
	for (s,p,o) in grafo.triples((nodo,None,None)):
		g.add((s,p,o))
		g+= expandirGrafoRec(grafo,o)
	return g

	