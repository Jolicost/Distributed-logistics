#! /bin/bash

trap "kill 0" EXIT

. directorio.config

echo "$usuarios" 

python AgenteUsuario.py --name Adrian --dhost $directorio --port 8001 --host $usuarios &

wait
