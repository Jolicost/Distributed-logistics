
from __future__ import print_function
from multiprocessing import Process
from flask import Flask, request, render_template
from time import sleep

app = Flask(__name__,template_folder="AgenteEnviador/templates")


@app.route("/")
def main_page():
    """
    El hola mundo de los servicios web
    :return:
    """
    return render_template('main.html')


if __name__ == "__main__":
    app.run()


def start_server():
    app.run()
