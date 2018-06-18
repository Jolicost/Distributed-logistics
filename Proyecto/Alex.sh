#! /bin/bash

trap "kill 0" EXIT

. directorio.config

./removeTurtle.sh

python juegosPrueba.py
python AgenteUsuario.py --name Alex --open --dhost $directorio --port 8000 &

wait
