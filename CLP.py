import threading
from opcua import Client, Server


def opcClientThread():
    pass

def opcServerThread():
    pass


def main():
    client = threading.Thread(target=opcClientThread)
    server = threading.Thread(target=opcServerThread)

    try:
        client.start()
        server.start()

    except Exception as e:
        print("Error starting threads:", e)



if __name__ == "__main__":
    main()