#! /bin/bash

trap "kill 0" EXIT

. directorio.config

python AgenteUsuario.py --name Alex --open --dhost $directorio --port 8000 &

wait
