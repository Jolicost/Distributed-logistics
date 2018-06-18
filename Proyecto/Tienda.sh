trap "kill 0" EXIT

./removeTurtle.sh

python juegosPrueba.py
python AgenteAdmisor.py --open --dhost 10.10.73.42 &
python AgenteBuscador.py --open --dhost 10.10.73.42 &
python AgenteDevolvedor.py --open --dhost 10.10.73.42 &
python AgenteMonetario.py --open --dhost 10.10.73.42 &
python AgenteOpinador.py --open --dhost 10.10.73.42 &
python AgenteReceptor.py --open --dhost 10.10.73.42 &

wait
