#!/bin/bash

echo "=== Iniciando bridge ==="
python3 bridge.py > /dev/null 2>&1 &
PID_BRIDGE=$!

sleep 1

echo "=== Iniciando CLP ==="
python3 CLP.py > /dev/null 2>&1 &
PID_CLP=$!

sleep 1  

echo "=== Iniciando Supervisório TCP ==="
python3 GUI.py > /dev/null 2>&1 &
PID_SUP=$!

sleep 1

echo "=== Iniciando MES server ==="
python3 serverMES.py > /dev/null 2>&1 &
PID_MES=$!

sleep 1

echo "=== Iniciando MES client ==="
python3 clientMES.py > /dev/null 2>&1 &
PID_MES_CL=$!

echo ""
echo "Processos iniciados:"
echo "  Bridge PID        = $PID_BRIDGE"
echo "  CLP PID           = $PID_CLP"
echo "  Supervisório PID  = $PID_SUP"
echo "  MES Server PID    = $PID_MES"
echo "  MES Client PID    = $PID_MES_CL"

echo ""
echo "Para parar tudo use:"
echo "  kill $PID_BRIDGE $PID_CLP $PID_SUP $PID_MES $PID_MES_CL"
