from opcua import Client
import time
from datetime import datetime

MES_SERVER_URL = "opc.tcp://localhost:4840/OPCChainedServer"

def main():
    print("[MES] Conectando ao servidor OPC encadeado...")
    client = Client(MES_SERVER_URL)
    client.connect()
    print("[MES] Conectado!")

    # Acessa o namespace
    root = client.get_objects_node()

    # Acha o objeto Drone do servidor encadeado
    drone = root.get_child(["2:Drone"])

    # Pega cada variável
    dX = drone.get_child(["2:DroneX"])
    dY = drone.get_child(["2:DroneY"])
    dZ = drone.get_child(["2:DroneZ"])

    tX = drone.get_child(["2:TargetX"])
    tY = drone.get_child(["2:TargetY"])
    tZ = drone.get_child(["2:TargetZ"])

    print("[MES] Variáveis encontradas. Iniciando leitura...")

    while True:
        # Lê valores
        dx = dX.get_value()
        dy = dY.get_value()
        dz = dZ.get_value()

        tx = tX.get_value()
        ty = tY.get_value()
        tz = tZ.get_value()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        # Monta linha
        log_line = f"{timestamp}, Drone=({dx:.3f},{dy:.3f},{dz:.3f}), Target=({tx:.3f},{ty:.3f},{tz:.3f})\n"

        # Salva no arquivo
        with open("mes.txt", "a") as f:
            f.write(log_line)

        print("[MES]", log_line.strip())

        # Frequência de leitura (200 ms)
        time.sleep(0.2)

if __name__ == "__main__":
    main()
