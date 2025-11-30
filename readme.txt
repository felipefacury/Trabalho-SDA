===============================
Sistema de Automação – Drone OPC UA
===============================

Este projeto integra:
- Simulação do drone (CoppeliaSim)
- CLP virtual (OPC UA + TCP)
- Supervisório em Python
- Servidor MES (OPC UA encadeado)
- Cliente MES (registro de dados)

-------------------------------
1. Requisitos
-------------------------------
Instale as dependências:

    pip install opcua
    pip install tkintermapview

Certifique-se também de ter:
- Python 3
- CoppeliaSim rodando com o Simulation Server em:
      opc.tcp://localhost:53530/OPCUA/SimulationServer
- Abrir o arquivo de simulação drone.ttt
- Configurar o objeto Drone no Simulation Server


-------------------------------
2. Como executar
-------------------------------

Todo o sistema pode ser iniciado usando o script:

    ./launch.sh

Este script inicia automaticamente:
- bridge.py
- CLP.py
- GUI.py (supervisório)
- serverMES.py
- clientMES.py

Nenhum log é salvo em arquivo; toda saída é suprimida.

Para interromper tudo:

    kill <PID1> <PID2> <PID3> ...

(os PIDs são mostrados ao rodar o script)

-------------------------------
3. Operação do Supervisório
-------------------------------

Ao abrir o GUI.py (via launch.sh):

- Ajuste o valor de "Step" para definir o deslocamento.
- Use os botões X+, X–, Y+, Y–, Z+, Z– para movimentar o alvo do drone.
- A posição atual é atualizada em tempo real no painel.
- O mapa exibe a localização atual do drone em 2D.

-------------------------------
4. MES
-------------------------------

O servidor MES replica as variáveis do servidor OPC principal
e disponibiliza em:

    opc.tcp://localhost:4840/OPCChainedServer

O cliente MES grava continuamente os valores em "mes.txt".

-------------------------------
5. Estrutura dos arquivos
-------------------------------

bridge.py       -> Sincroniza simulador <-> OPC UA principal  
CLP.py          -> Cliente OPC + Servidor TCP  
GUI.py          -> Supervisório (HMI)  
serverMES.py    -> Servidor OPC UA encadeado  
clientMES.py    -> Cliente MES (gera histórico)  
launch.sh       -> Inicia todo o sistema  



