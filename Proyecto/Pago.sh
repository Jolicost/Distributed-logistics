trap "kill 0" EXIT

./removeTurtle.sh

python juegosPrueba.py
python ServicioPago.py --open --dhost 10.10.73.42 &

wait
