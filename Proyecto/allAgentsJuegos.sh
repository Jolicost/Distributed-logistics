trap "kill 0" EXIT

./removeTurtle.sh

python DirectorioAgentes.py &
sleep 1.5

python juegosPrueba.py
python editorCentrosLogisticos.py --port 7000 &
python editorPersonas.py --port 7001 &
python AgenteUsuario.py --name Alex -- port 8000 &
python AgenteUsuario.py --name Adrian --port 8001 &
python AgenteAdmisor.py --port 8010 &
python AgenteBuscador.py --port 8011 &
python AgenteEmpaquetador.py --port 8050 --name Capellades &
python AgenteEmpaquetador.py --port 8051 --name Igualada &
python AgenteOpinador.py --port 8012 &
python AgenteReceptor.py --port 8013 &
python AgenteVendedorExterno.py --name VendedorA --port 8020 &

python AgenteMonetario.py --port 8080 &
python ServicioPago.py --port 8081 &
python AgenteEnviador.py --name Capellades --port 8060 &
python AgenteEnviador.py --name Igualada --port 8061 &

python AgenteTransportista.py --name TransportistaA --port 8040 &
python AgenteTransportista.py --name TransportistaB --port 8041 &
python AgenteTransportista.py --name TransportistaC --port 8042 &

wait