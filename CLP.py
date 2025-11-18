import threading
from opcua import Client as opcClient
from opcua import ua
import socket

OPCUA_URL   = "opc.tcp://localhost:53530/OPCUA/SimulationServer"

dx:float = 0.0
dy:float = 0.0
dz:float = 0.0

tz:float = 0.0
tx:float = 0.0
ty:float = 0.0

mutex:threading.Lock = threading.Lock()
mutex2:threading.Lock = threading.Lock()

def getCoordinates(client:opcClient) -> tuple[float, float, float]:
    root = client.get_objects_node()
    drone_folder = None
    try:
        drone_folder = root.get_child(["3:Drone"])
    except Exception:
        # fallback: varrer filhos e procurar "Drone"
        for n in root.get_children():
            try:
                name = n.get_browse_name().Name
                if name.lower() == "drone":
                    drone_folder = n
                    break
            except Exception:
                pass
    if drone_folder is None:
        raise RuntimeError("Não encontrei a pasta 'Drone' no servidor OPC UA.")

    # Mapeie variáveis por nome (case-insensitive)
    name_to_node = {}
    for v in drone_folder.get_children():
        try:
            nm = v.get_browse_name().Name
            name_to_node[nm.lower()] = v
        except Exception:
            pass

    # Esperadas (ajuste aqui se seus nomes diferirem)
    dX = name_to_node.get("dronex")
    dY = name_to_node.get("droney")
    dZ = name_to_node.get("dronez")

    if not all([dX, dY, dZ]):
        found = ", ".join(sorted(name_to_node.keys()))
        raise RuntimeError(
            "Variáveis esperadas não encontradas. "
            "Quero DroneX, DroneY, DroneZ. "
            f"Encontradas: {found}"
        )
    
    return (dX, dY, dZ)


def writeCoordinates(x:float, y:float, z:float, client:opcClient):
    root = client.get_objects_node()
    drone_folder = None
    try:
        drone_folder = root.get_child(["3:Drone"])
    except Exception:
        # fallback: varrer filhos e procurar "Drone"
        for n in root.get_children():
            try:
                name = n.get_browse_name().Name
                if name.lower() == "drone":
                    drone_folder = n
                    break
            except Exception:
                pass
    if drone_folder is None:
        raise RuntimeError("Não encontrei a pasta 'Drone' no servidor OPC UA.")

    tx = drone_folder.get_child(["3:TargetX"])
    ty = drone_folder.get_child(["3:TargetY"])
    tz = drone_folder.get_child(["3:TargetZ"])

    tipo_do_dado = ua.VariantType.Float
    tx.set_value(x, tipo_do_dado)
    ty.set_value(y, tipo_do_dado)
    tz.set_value(z, tipo_do_dado)
    

def opcClientThread(event:threading.Event):
    try:
        global tx, ty, tz, dx, dy, dz

        client = opcClient(OPCUA_URL)
        client.connect()
        while not event.is_set():
            (px, py, pz) = getCoordinates(client)
            with mutex2:
                dx = px.get_value()
                dy = py.get_value()
                dz = pz.get_value()
            # Control logic he
            with mutex:
                writeCoordinates(tx, ty, tz, client)
            
    except Exception as e:
        print("Error in OPC UA Client thread:", e)
    finally:
        print("Disconnecting OPC UA client...")
        client.disconnect()


def tcpServerThread(event:threading.Event):
    try:
        global tx, ty, tz, dx, dy, dz

        tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpSocket.bind(("localhost", 5005))
        tcpSocket.settimeout(1.0)

        while not event.is_set():
            tcpSocket.listen()
            try:
                conn, addr = tcpSocket.accept()
            except socket.timeout:
                continue
            with conn:
                print("Connected by", addr)
                data = conn.recv(1024)
                if not data:
                    continue
                print("Received data:", data)
                with mutex:
                    x_str, y_str, z_str = data.decode('utf-8').split(',')
                    tx = float(x_str)
                    ty = float(y_str)
                    tz = float(z_str)
                # Process data as needed
                response = b"ACK"
                conn.sendall(response)

    except Exception as e:
        print("Error in TCP Server thread:", e)
    finally:
        print("Shutting down TCP server...")
        tcpSocket.close()

def main():
    event = threading.Event()
    #server = threading.Thread(target=tcpServerThread)

    try:
        client = threading.Thread(target=opcClientThread, args=(event,))
        server = threading.Thread(target=tcpServerThread, args=(event,))
        client.start()
        server.start()

        while client.is_alive():
            client.join(timeout=1.0)
        while server.is_alive():
            server.join(timeout=1.0)

    except KeyboardInterrupt:
        event.set()

    except Exception as e:
        print("Error starting threads:", e)



if __name__ == "__main__":
    main()