#! /bin/bash

trap "kill 0" EXIT

. directorio.config

python AgenteAdmisor.py --open --dhost $directorio --host $directorio &
python AgenteBuscador.py --open --dhost $directorio --host $directorio &
python AgenteDevolvedor.py --open --dhost $directorio --host $directorio &
python AgenteMonetario.py --open --dhost $directorio --host $directorio &
python AgenteOpinador.py --open --dhost $directorio --host $directorio &
python AgenteReceptor.py --open --dhost $directorio --host $directorio &

wait
