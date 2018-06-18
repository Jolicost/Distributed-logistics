#! /bin/bash

trap "kill 0" EXIT

. directorio.config

./removeTurtle.sh

python juegosPrueba.py
python AgenteEmpaquetador.py --name Capellades --open --dhost $directorio --port 7010 &
python AgenteEnviador.py --name Capellades --open --dhost $directorio --port 7000 &

wait
