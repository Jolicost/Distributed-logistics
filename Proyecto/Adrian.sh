#! /bin/bash

trap "kill 0" EXIT

. directorio.config

python AgenteUsuario.py --name Adrian --open --dhost $directorio --port 8001 --host $usuarios &

wait
