trap "kill 0" EXIT

./removeTurtle.sh

python juegosPrueba.py
python editorCentrosLogisticos.py &
python editorPersonas.py &
python AgenteUsuario.py --name Alex &
python AgenteAdmisor.py &
python AgenteBuscador.py &
python AgenteEmpaquetador.py --port 8050 --name Capellades &
python AgenteEmpaquetador.py --port 8051 --name Igualada &
python AgenteOpinador.py &
python AgenteReceptor.py &
python AgenteVendedorExterno.py --name VendedorA &
#python AgenteEnviador.py --name Capellades --port 8061 &
#python AgenteEnviador.py --name Igualada --port 8060 &
python AgenteTransportista.py --name TransportistaA &

wait