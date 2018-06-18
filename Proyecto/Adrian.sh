#! /bin/bash

trap "kill 0" EXIT

. directorio.config

./removeTurtle.sh

python juegosPrueba.py
python AgenteUsuario.py --name Adrian --open --dhost $directorio &

wait
