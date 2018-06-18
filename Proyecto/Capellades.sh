#! /bin/bash

trap "kill 0" EXIT

. directorio.config

python AgenteEmpaquetador.py --name Capellades --open --port 7010 &
python AgenteEnviador.py --name Capellades --open --port 7000 &

wait
