
from __future__ import print_function
from multiprocessing import Process
from flask import Flask, request, render_template
from time import sleep

#Cambiamos la ruta por defecto de los templates para que sea dentro de los ficheros del agente
app = Flask(__name__,template_folder="AgenteVendedorExterno/templates")


@app.route("/")
def main_page():
    """
    Pagina principal. No hay acciones extras.
    """
    return render_template('main.html')


@app.route("/vender")
def pag():
    """
    Mostrar pagina para poner un producto a la venda
    """
    return render_template('vender.html')


@app.route("/poner_venda", methods=['GET'])
def poner_venda():
    '''
    enviar datos a la tienda
    '''
    return render_template('render_text.html',text=str(request.args['nombre']))


if __name__ == "__main__":
    app.run()


def start_server():
    app.run()