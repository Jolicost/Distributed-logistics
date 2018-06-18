#! /bin/bash

trap "kill 0" EXIT

. directorio.config

./removeTurtle.sh

python juegosPrueba.py
python AgenteTransportista.py --name TransportistaC --open --dhost $directorio --port 8082 &

wait
