trap "kill 0" EXIT

./removeTurtle.sh

python juegosPrueba.py
python AgenteEmpaquetador.py --name Montserrat --open --dhost 10.10.73.42 &
python AgenteEnviador.py --name Montserrat --open --dhost 10.10.73.42 &

wait
