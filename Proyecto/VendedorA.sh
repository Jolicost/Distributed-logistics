#! /bin/bash

trap "kill 0" EXIT

. directorio.config

python AgenteVendedorExterno.py --name VendedorA --dhost $directorio --port 8090 --host $directorio &

wait
