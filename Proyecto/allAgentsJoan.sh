trap "kill 0" EXIT

./removeTurtle.sh

python juegosPrueba.py
python DirectorioAgentes.py &
sleep 1.5

python AgenteEnviador.py --name Capellades --port 8020 &
python AgenteEnviador.py --name Igualada --port 8021 &
python AgenteTransportista.py --name TransportistaA --port 8030 &
python AgenteTransportista.py --name TransportistaB --port 8031 &
python AgenteTransportista.py --name TransportistaC --port 8032 &
python AgenteMonetario.py --port 8001 &
python ServicioPago.py --port 8002 &
python AgenteReceptor.py --port 8005 &

wait