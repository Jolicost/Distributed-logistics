#! /bin/bash

trap "kill 0" EXIT

. directorio.config

python AgenteAdmisor.py --dhost $directorio --open &
python AgenteBuscador.py --dhost $directorio --open &
python AgenteDevolvedor.py --dhost $directorio --open &
python AgenteMonetario.py --dhost $directorio --open &
python AgenteOpinador.py --dhost $directorio --open &
python AgenteReceptor.py --dhost $directorio --open &

wait
