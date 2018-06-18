trap "kill 0" EXIT

./removeTurtle.sh

python DirectorioAgentes.py --open &

wait
