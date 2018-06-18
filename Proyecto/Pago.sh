#! /bin/bash

trap "kill 0" EXIT

. directorio.config

python ServicioPago.py --open --dhost $directorio --host $directorio  &

wait
