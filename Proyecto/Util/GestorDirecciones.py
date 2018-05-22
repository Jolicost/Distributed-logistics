import json
import sys

def get_data():
	data = {}
	data['agente_usuario'] = {
		'dir':'localhost',
		'port':8000
	}
	data['agente_receptor'] = {
		'dir':'localhost',
		'port':8000
	}
	data['agente_admisor'] = {
		'dir':'localhost',
		'port':8000
	}
	return data


def write_json(file,data):
	with open(file,'w') as out:
		json.dump(data,out,indent=4)

def read_json(file):
	data = None
	with open(file,'r') as f:
		data = json.load(f)
	return data


if __name__ == "__main__":
	if (len(sys.argv) < 2):
		raise Exception("you need to specify the output file")
	output_file = sys.argv[1]
	data = get_data()
	write_json(output_file,data)
	print "Successfully wrote the json config file into" , output_file
	print "The json structure is the following: "
	json = read_json(output_file)
	print json
