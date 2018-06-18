trap "kill 0" EXIT

./removeTurtle.sh

python juegosPrueba.py
python AgenteVendedorExterno.py --name VendedorA --open --dhost 10.10.73.42 &

wait
