import threading
from opcua import Client as opcClient
from opcua import ua,Server
import time
import queue

mesQueue:queue.Queue[tuple[float, float, float,float,float,float]] = queue.Queue()
OPCUA_URL   = "opc.tcp://localhost:53530/OPCUA/SimulationServer"


def getCoordinates(client:opcClient) -> tuple[float, float, float,float,float,float]:
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
    targetX = name_to_node.get("targetx")
    targetY = name_to_node.get("targety")
    targetZ = name_to_node.get("targetz")

    if not all([dX, dY, dZ]):
        found = ", ".join(sorted(name_to_node.keys()))
        raise RuntimeError(
            "Variáveis esperadas não encontradas. "
            "Quero DroneX, DroneY, DroneZ, TargetX, TargetY, TargetZ. "
            f"Encontradas: {found}"
        )
    
    return (dX, dY, dZ,targetX,targetY,targetZ)

def opcClientThread(event:threading.Event):
    try:
        client = opcClient(OPCUA_URL)
        client.connect()
        while not event.is_set():
            (px, py, pz,tx,ty,tz) = getCoordinates(client)
            if not mesQueue.full():
                dx = px.get_value()
                dy = py.get_value()
                dz = pz.get_value()
                tax = tx.get_value()
                tay = ty.get_value()
                taz = tz.get_value()
                mesQueue.put((dx, dy, dz,tax,tay,taz))
            
    except Exception as e:
        print("Error in OPC UA Client thread:", e)
    finally:
        print("Disconnecting OPC UA client...")
        client.disconnect()
        

def opcServerThread(event: threading.Event):
    server = Server()

    # Endpoint do servidor OPC encadeado
    server.set_endpoint("opc.tcp://0.0.0.0:4840/OPCChainedServer")

    # Namespace (pode ser qualquer nome)
    uri = "MESChainedServer"
    idx = server.register_namespace(uri)

    # Pasta raiz
    objects = server.get_objects_node()

    # Cria objeto Drone
    drone = objects.add_object(idx, "Drone")

    # Variáveis expostas pelo novo servidor
    dX = drone.add_variable(idx, "DroneX", 0.0)
    dY = drone.add_variable(idx, "DroneY", 0.0)
    dZ = drone.add_variable(idx, "DroneZ", 0.0)

    tX = drone.add_variable(idx, "TargetX", 0.0)
    tY = drone.add_variable(idx, "TargetY", 0.0)
    tZ = drone.add_variable(idx, "TargetZ", 0.0)

    # Habilitar escrita (caso precise depois)
    dX.set_writable()
    dY.set_writable()
    dZ.set_writable()

    tX.set_writable()
    tY.set_writable()
    tZ.set_writable()

    print("[OPC SERVER] Servidor MES iniciado em opc.tcp://localhost:4840")

    # Inicia o servidor
    server.start()

    try:
        while not event.is_set():
            if not mesQueue.empty():
                (dx, dy, dz, tx_val, ty_val, tz_val) = mesQueue.get()

                # Atualiza as variáveis do servidor
                dX.set_value(dx)
                dY.set_value(dy)
                dZ.set_value(dz)

                tX.set_value(tx_val)
                tY.set_value(ty_val)
                tZ.set_value(tz_val)

            time.sleep(0.05)

    except Exception as e:
        print("[OPC SERVER] Erro:", e)

    finally:
        print("[OPC SERVER] Encerrando servidor MES...")
        server.stop()


def main():
    event = threading.Event()
    try:
        client = threading.Thread(target=opcClientThread, args=(event,))
        server = threading.Thread(target=opcServerThread, args=(event,))
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