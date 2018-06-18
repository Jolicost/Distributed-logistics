#! /bin/bash

trap "kill 0" EXIT

. directorio.config

./removeTurtle.sh

python juegosPrueba.py
python AgenteEmpaquetador.py --name Montserrat --open --dhost $directorio --port 7012 &
python AgenteEnviador.py --name Montserrat --open --dhost $directorio --port 7002 &

wait
