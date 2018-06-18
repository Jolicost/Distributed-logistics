#! /bin/bash

trap "kill 0" EXIT

. directorio.config

./removeTurtle.sh

python juegosPrueba.py
python AgenteEmpaquetador.py --name Igualada --open --dhost $directorio &
python AgenteEnviador.py --name Igualada --open --dhost $directorio &

wait
