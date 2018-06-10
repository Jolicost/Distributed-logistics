import datetime
from time import gmtime, strftime

def getCurrentDateTime():
	return strftime("%Y-%m-%d %H:%M:%S", gmtime())


def stringToDateTime(string):
	return parse(string)