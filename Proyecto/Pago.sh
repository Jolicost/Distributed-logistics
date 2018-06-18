#! /bin/bash

trap "kill 0" EXIT

. directorio.config

./removeTurtle.sh

python juegosPrueba.py
python ServicioPago.py --open --dhost $directorio &

wait
