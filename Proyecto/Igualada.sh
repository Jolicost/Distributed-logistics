#! /bin/bash

trap "kill 0" EXIT

. directorio.config

./removeTurtle.sh

python juegosPrueba.py
python AgenteEmpaquetador.py --name Igualada --open --dhost $directorio --port 7011 &
python AgenteEnviador.py --name Igualada --open --dhost $directorio --port 7001 &

wait
