trap "kill 0" EXIT

./removeTurtle.sh

python juegosPrueba.py
python AgenteEmpaquetador.py --name Capellades --open --dhost 10.10.73.42 &
python AgenteEnviador.py --name Capellades --open --dhost 10.10.73.42 &

wait
