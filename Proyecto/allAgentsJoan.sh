trap "kill 0" EXIT

python editorCentrosLogisticos.py &
python AgenteUsuario.py --name Joan &
python AgenteAdmisor.py &
python AgenteBuscador.py &
python AgenteEmpaquetador.py --port 8050 --name Vallecas &
python AgenteEmpaquetador.py --port 8051 --name Capellades &
python AgenteOpinador.py &
python AgenteReceptor.py &
python AgenteVendedorExterno.py --name 324 &
python AgenteEnviador.py --name Vallecas &
python AgenteTransportista.py --name Transports_Agile &

wait