#!/bin/bash

SESSION="drone_system"

# Remove sessão antiga
tmux kill-session -t $SESSION 2>/dev/null

# Cria sessão + primeiro painel (pane 0)
tmux new-session -d -s $SESSION -n main

# Criar todos os 6 painéis primeiro
tmux split-window -v -t $SESSION:0        # pane 1
tmux select-pane -t $SESSION:0.0
tmux split-window -h -t $SESSION:0.0      # pane 2
tmux select-pane -t $SESSION:0.1
tmux split-window -h -t $SESSION:0.1      # pane 3
tmux select-pane -t $SESSION:0.2
tmux split-window -v -t $SESSION:0.2      # pane 4
tmux select-pane -t $SESSION:0.3
tmux split-window -v -t $SESSION:0.3      # pane 5

# Agora temos 6 painéis: 0,1,2,3,4,5

###########################################
# Inicialização com dependências + delays #
###########################################

# 1) bridge.py (independente)
tmux send-keys -t $SESSION:0.0 "python3 bridge.py" C-m

# 2) CLP.py
tmux send-keys -t $SESSION:0.1 "python3 CLP.py" C-m

# ------ Espera CLP subir ------
sleep 2

# 3) GUI.py (cliente TCP, depende do CLP)
tmux send-keys -t $SESSION:0.2 "python3 GUI.py" C-m

# 4) serverMES.py
tmux send-keys -t $SESSION:0.3 "python3 serverMES.py" C-m

# ------ Espera MES server subir ------
sleep 2

# 5) clientMES.py (depende do serverMES)
tmux send-keys -t $SESSION:0.4 "python3 clientMES.py" C-m

# 6) shell livre
tmux send-keys -t $SESSION:0.5 "bash" C-m

# Entra no tmux
tmux attach -t $SESSION

