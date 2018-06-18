#! /bin/bash

trap "kill 0" EXIT

. directorio.config

./removeTurtle.sh

python juegosPrueba.py
python AgenteEmpaquetador.py --name Montserrat --open --dhost $directorio &
python AgenteEnviador.py --name Montserrat --open --dhost $directorio &

wait
