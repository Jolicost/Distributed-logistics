#! /bin/bash

trap "kill 0" EXIT

. directorio.config

./removeTurtle.sh

python juegosPrueba.py
python AgenteAdmisor.py --open --dhost $directorio &
python AgenteBuscador.py --open --dhost $directorio &
python AgenteDevolvedor.py --open --dhost $directorio &
python AgenteMonetario.py --open --dhost $directorio &
python AgenteOpinador.py --open --dhost $directorio &
python AgenteReceptor.py --open --dhost $directorio &

wait
