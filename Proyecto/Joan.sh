#! /bin/bash

trap "kill 0" EXIT

. directorio.config

./removeTurtle.sh

python juegosPrueba.py
python AgenteUsuario.py --name Joan --open --dhost $directorio --port 8002 &

wait
