#! /bin/bash

trap "kill 0" EXIT

. directorio.config

./removeTurtle.sh

python juegosPrueba.py
python AgenteTransportista.py --name TransportistaB --open --dhost $directorio &

wait
