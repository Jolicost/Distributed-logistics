trap "kill 0" EXIT

./removeTurtle.sh

python juegosPrueba.py
python AgenteTransportista.py --name TransportistaA --open --dhost 10.10.73.42 &

wait
