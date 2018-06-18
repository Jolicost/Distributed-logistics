#! /bin/bash

trap "kill 0" EXIT

. directorio.config

python AgenteEmpaquetador.py --name Montserrat --open --dhost $directorio --port 7012 &
python AgenteEnviador.py --name Montserrat --open --dhost $directorio --port 7002 &

wait
