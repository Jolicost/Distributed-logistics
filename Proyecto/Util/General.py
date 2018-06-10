import datetime
import argparse
from time import gmtime, strftime
import socket

def getCurrentDateTime():
	return strftime("%Y-%m-%d %H:%M:%S", gmtime())


def stringToDateTime(string):
	return parse(string)



def getArguments(dir_host='localhost',dir_port=9000,my_port=8000,name='default'):

	parser = argparse.ArgumentParser()
	parser.add_argument('--open', help="Define si el servidor esta abierto al exterior o no", action='store_true',
                    default=False)
	parser.add_argument('--port', type=int, help="Puerto de comunicacion del agente")
	parser.add_argument('--dhost', default='localhost', help="Host del agente de directorio")
	parser.add_argument('--dport', type=int, help="Puerto de comunicacion del agente de directorio")
	parser.add_argument('--name', type=str, help="Nombre del agente (Sin URI)")


	# parsing de los parametros de la linea de comandos
	args = parser.parse_args()

	ret = {}
	# Configuration stuff
	if args.port is None:
	    ret['port'] = my_port
	else:
	    ret['port'] = args.port

	if args.open is None:
	    ret['host'] = '0.0.0.0'
	else:
	    ret['host'] = 'localhost'

	if args.dport is None:
	    ret['dir_port'] = dir_port
	else:
	    ret['dir_port'] = args.dport

	if args.dhost is None:
	    ret['dir_host'] = dir_host
	else:
	    ret['dir_host'] = args.dhost

	if args.name is None:
		ret['name'] = name
	else:
		ret['name'] = args.name

	return ret