#! /bin/bash

trap "kill 0" EXIT

. directorio.config

python AgenteAdmisor.py --dhost $directorio --host $directorio &
python AgenteBuscador.py --dhost $directorio --host $directorio &
python AgenteDevolvedor.py --dhost $directorio --host $directorio &
python AgenteMonetario.py --dhost $directorio --host $directorio &
python AgenteOpinador.py --dhost $directorio --host $directorio &
python AgenteReceptor.py --dhost $directorio --host $directorio &

wait
