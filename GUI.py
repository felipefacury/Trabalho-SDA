import tkinter as tk
from tkinter import messagebox
import threading
import socket
import queue
import time


cmdQueue:queue.Queue[tuple[float, float, float]] = queue.Queue(50)


posQueue:queue.Queue[tuple[float, float, float]] = queue.Queue(50)

class DroneGUI:
    def __init__(self, master):
        self.master = master
        master.title("Controle de Jogging do Drone (3D)")
        master.geometry("800x480")

        # --- Variáveis de Comunicação (mantidas) ---
        self.cmd_x = tk.DoubleVar(value=0.0)
        self.cmd_y = tk.DoubleVar(value=0.0)
        self.cmd_z = tk.DoubleVar(value=1.5)
        
        self.pos_x = 0.0 
        self.pos_y = 0.0
        self.pos_z = 0.0

        
        # --- Variáveis de Step (Agora são a principal entrada) ---
        self.step_xy = tk.StringVar(value="0.5") # Step para X e Y
        self.step_z = tk.StringVar(value="0.1")  # Step para Z

        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)

        self.setup_control_panel()
        self.setup_map_panel()
        
        # Inicia o loop de atualização do mapa
        self.master.after(100, self.simulate_external_update)

    def move_drone(self, axis, direction):
        """
        Função central que calcula o novo comando baseado no clique do botão e no step.
        axis: 'X', 'Y', ou 'Z'
        direction: +1 (aumentar) ou -1 (diminuir)
        """
        try:
            # 1. Obter o valor do STEP e o comando atual
            if axis in ['X', 'Y']:
                step_value = float(self.step_xy.get())
                current_cmd = self.cmd_x if axis == 'X' else self.cmd_y
            else: # Z
                step_value = float(self.step_z.get())
                current_cmd = self.cmd_z
                
            # 2. Calcular e aplicar o novo valor
            novo_valor = current_cmd.get() + (step_value * direction)
            
            # Limites de segurança (opcional, mas bom para controle)
            if axis in ['X', 'Y']:
                 if not -50 <= novo_valor <= 50: return # Limita X/Y
            elif axis == 'Z':
                 if not 0 <= novo_valor <= 20: return # Limita Z (altura)
            
            current_cmd.set(novo_valor)

            if not cmdQueue.full():
                cmdQueue.put((self.cmd_x.get(), self.cmd_y.get(), self.cmd_z.get()))

            print(f"Comando {axis} enviado: {novo_valor:.2f}")

        except ValueError:
            messagebox.showerror("Erro de Step", "O valor do Step deve ser um número válido.")


    def setup_control_panel(self):
        """ Configura os botões de jogging e campos de step. """
        control_frame = tk.LabelFrame(self.master, text="Controle Incremental (Jogging)", padx=10, pady=10)
        control_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # --- 1. Entrada do Step Size ---
        step_frame = tk.Frame(control_frame)
        step_frame.grid(row=0, column=0, columnspan=2, pady=10)
        
        tk.Label(step_frame, text="Step XY:").pack(side=tk.LEFT)
        self.entry_step_xy = tk.Entry(step_frame, textvariable=self.step_xy, width=8)
        self.entry_step_xy.pack(side=tk.LEFT, padx=5)
        
        tk.Label(step_frame, text="Step Z:").pack(side=tk.LEFT)
        self.entry_step_z = tk.Entry(step_frame, textvariable=self.step_z, width=8)
        self.entry_step_z.pack(side=tk.LEFT, padx=5)

        # --- 2. Painel de Movimento XY (Grid 3x3) ---
        xy_frame = tk.LabelFrame(control_frame, text="XY - Horizontal")
        xy_frame.grid(row=1, column=0, padx=10, pady=10)
        
        # Y Positivo (Para Cima)
        tk.Button(xy_frame, text="↑ Y+", width=5, command=lambda: self.move_drone('Y', 1)).grid(row=0, column=1)
        
        # X Negativo (Esquerda)
        tk.Button(xy_frame, text="← X-", width=5, command=lambda: self.move_drone('X', -1)).grid(row=1, column=0)
        
        # Centro (Pode ser um botão de 'Parar' ou 'Home')
        tk.Label(xy_frame, text="  XY  ").grid(row=1, column=1)
        
        # X Positivo (Direita)
        tk.Button(xy_frame, text="X+ →", width=5, command=lambda: self.move_drone('X', 1)).grid(row=1, column=2)
        
        # Y Negativo (Para Baixo)
        tk.Button(xy_frame, text="↓ Y-", width=5, command=lambda: self.move_drone('Y', -1)).grid(row=2, column=1)

        # --- 3. Painel de Movimento Z (Vertical) ---
        z_frame = tk.LabelFrame(control_frame, text="Z - Vertical")
        z_frame.grid(row=1, column=1, padx=10, pady=10)
        
        # Z Positivo (Subir)
        tk.Button(z_frame, text="▲ Z+", width=5, command=lambda: self.move_drone('Z', 1)).pack(pady=5)
        
        # Z Negativo (Descer)
        tk.Button(z_frame, text="▼ Z-", width=5, command=lambda: self.move_drone('Z', -1)).pack(pady=5)

        # --- 4. Exibição dos Comandos (Saída) ---
        cmd_frame = tk.Frame(control_frame)
        cmd_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        tk.Label(cmd_frame, text="Target X:").pack(side=tk.LEFT)
        tk.Label(cmd_frame, textvariable=self.cmd_x).pack(side=tk.LEFT, padx=5)
        tk.Label(cmd_frame, text="Y:").pack(side=tk.LEFT)
        tk.Label(cmd_frame, textvariable=self.cmd_y).pack(side=tk.LEFT, padx=5)
        tk.Label(cmd_frame, text="Z:").pack(side=tk.LEFT)
        tk.Label(cmd_frame, textvariable=self.cmd_z).pack(side=tk.LEFT, padx=5)
        tk.Label(control_frame, text="^ Comandos (OUTPUT) ^").grid(row=3, column=0, columnspan=2)

        if not cmdQueue.empty():
            (x, y, z) = cmdQueue.get()
            self.cmd_x.set(x)
            self.cmd_y.set(y)
            self.cmd_z.set(z)
        else:
            self.cmd_x.set(0.0)
            self.cmd_y.set(0.0) 
            self.cmd_z.set(1.5)


    # --- Métodos de Mapa e Simulação (Mantidos) ---
    def setup_map_panel(self):
        """ Configura o Canvas para o mapa 2D (X vs Y). """
        map_frame = tk.LabelFrame(self.master, text="Mapa 2D (Posição X vs Y)", padx=10, pady=10)
        map_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.map_canvas = tk.Canvas(map_frame, width=400, height=350, bg="light gray")
        self.map_canvas.pack(expand=True, fill="both")
        
        self.center_x, self.center_y = 200, 175
        self.map_canvas.create_line(self.center_x, 0, self.center_x, 350, fill="black", dash=(4, 4))
        self.map_canvas.create_line(0, self.center_y, 400, self.center_y, fill="black", dash=(4, 4))
        
        self.drone_marker = self.map_canvas.create_oval(self.center_x - 5, self.center_y - 5, 
                                                        self.center_x + 5, self.center_y + 5, 
                                                        fill="red")

        self.pos_label = tk.Label(map_frame, text=f"POS: X:{self.pos_x:.1f}, Y:{self.pos_y:.1f}, Z:{self.pos_z:.1f}")
        self.pos_label.pack(pady=5)
        tk.Label(map_frame, text="^ Posição Real (INPUT) ^").pack()
        

    def update_map(self):
        """ Atualiza o mapa com a posição real (self.pos_x, self.pos_y). """
        scale = 3.0
        canvas_x = self.center_x + self.pos_x * scale
        canvas_y = self.center_y - self.pos_y * scale 

        self.map_canvas.coords(self.drone_marker, 
                               canvas_x - 5, canvas_y - 5, 
                               canvas_x + 5, canvas_y + 5)
        
        self.pos_label.config(text=f"POS: X:{self.pos_x:.1f}, Y:{self.pos_y:.1f}, Z:{self.pos_z:.1f}")


    def simulate_external_update(self):
        """ Simula a recepção dos 3 valores de posição de um código externo. """
        
        # Tenta pegar o valor do step XY, se falhar (não for um número), usa 0.1
        # try:
        #     step = abs(float(self.step_xy.get())) * 0.1 
        # except ValueError:
        #     step = 0.5 

        if not posQueue.empty():
            (dx, dy, dz) = posQueue.get()
            self.pos_x = dx
            self.pos_y = dy
            self.pos_z = dz

        print(f"Posição atual recebida: X={self.pos_x:.2f}, Y={self.pos_y:.2f}, Z={self.pos_z:.2f}")

        # # O drone (pos_x/y) se move em direção ao alvo (cmd_x/y)
        # if abs(self.pos_x - self.cmd_x.get()) > step:
        #      self.pos_x += step if self.cmd_x.get() > self.pos_x else -step
        # else:
        #      self.pos_x = self.cmd_x.get()
             
        # if abs(self.pos_y - self.cmd_y.get()) > step:
        #     self.pos_y += step if self.cmd_y.get() > self.pos_y else -step
        # else:
        #     self.pos_y = self.cmd_y.get()
            
        # # Z é movido diretamente para simplificar
        # self.pos_z = self.cmd_z.get() 

        self.update_map()
        self.master.after(100, self.simulate_external_update)


def guiThread(event:threading.Event):
    root = tk.Tk()
    app = DroneGUI(root)
    root.mainloop() 

def connection_alive(client:socket.socket) -> bool:
    try:
        client.getpeername()
        return True
    except OSError:
        return False

def networkThread(event:threading.Event):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    
    try:
        while not event.is_set():
            if not connection_alive(client):
                try:
                    client.connect(("localhost", 5055))
                except ConnectionRefusedError:
                    time.sleep(1)
                    continue

            data = client.recv(1024)
            #print("Received response:", data.decode('utf-8'))
            x_str, y_str, z_str = data.decode('utf-8').split(',')
            dx = float(x_str)
            dy = float(y_str)
            dz = float(z_str)
            if not posQueue.full():
                posQueue.put((dx, dy, dz))
                print(f"Updated position to: ({dx}, {dy}, {dz})")

            if not cmdQueue.empty():
                (x, y, z) = cmdQueue.get(timeout=1.0)
                message = f"{x},{y},{z}".encode('utf-8')
            else:
                message = "nop".encode('utf-8')
                

            #print("Sending:", message)
            client.sendall(message)


    except Exception as e:
        print("Communication error:", e)
    finally:
        print("Closing connection...")
        client.close() 

def historyThread(event:threading.Event):
    with open("historiador.txt", "w") as f:
        f.write("Timestamp, X, Y, Z\n")

    while not event.is_set():
        with open("historiador.txt", "a") as f:
            if not posQueue.empty():
                (x, y, z) = posQueue.get()
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                f.write(f"{timestamp}, {x:.2f}, {y:.2f}, {z:.2f}\n")

def main():
    event = threading.Event()
    netThread = threading.Thread(target=networkThread, args=(event,))
    gThread = threading.Thread(target=guiThread, args=(event,))
    hThread = threading.Thread(target=historyThread, args=(event,))

    try:
        netThread.start()
        gThread.start()
        hThread.start()

        while netThread.is_alive():
            netThread.join(timeout=1.0)
        while gThread.is_alive():
            gThread.join(timeout=1.0)
        while hThread.is_alive():
            hThread.join(timeout=1.0)
    except KeyboardInterrupt:
        print("Exiting...")
        event.set()
    except Exception as e:
        print("Error starting threads:", e)


if __name__ == "__main__":

    main()