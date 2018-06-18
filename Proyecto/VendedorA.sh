#! /bin/bash

trap "kill 0" EXIT

. directorio.config

./removeTurtle.sh

python juegosPrueba.py
python AgenteVendedorExterno.py --name VendedorA --open --dhost $directorio &

wait
