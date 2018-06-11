trap "kill 0" EXIT

python AgenteEnviador.py --name Capellades --port 8020 &
python AgenteEnviador.py --name Igualada --port 8021 &
python AgenteTransportista.py --name TransportistaA --port 8030 &
python AgenteTransportista.py --name TransportistaB --port 8031 &
python AgenteTransportista.py --name TransportistaC --port 8032&

wait