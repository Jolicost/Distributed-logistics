
from __future__ import print_function
from multiprocessing import Process
from flask import Flask, request, render_template
from time import sleep

app = Flask(__name__)


@app.route("/")
def main_page():
    """
    El hola mundo de los servicios web
    :return:
    """
    return render_template('main.html')


@app.route("/buscar")
def pag():
    """
    Entrada que sirve una pagina de web que cuenta hasta 10
    :return:
    """
    return render_template('buscarProductos.html')


@app.route("/buscarProductos", methods=['GET','POST'])
def buscarProductos():
    resultado = ["peras","manzanas","zanahorias"]

    return render_template(
        'resultadoBusqueda.html',
        criterio=request.args['criterio'],
        values=resultado
    )


if __name__ == "__main__":
    app.run()


def start_server():
    app.run()