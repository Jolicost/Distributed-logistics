#! /bin/bash

trap "kill 0" EXIT

. directorio.config

./removeTurtle.sh

python juegosPrueba.py
python AgenteTransportista.py --name TransportistaA --open --dhost $directorio --port 8080 &

wait
