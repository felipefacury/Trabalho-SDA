import socket


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect(("localhost", 5005))
    except Exception as e:
        print("Connection error:", e)
        return
    
    try:
        while True:
            user = input("Enter new coordinates (x y z), or 'quit' to exit: ")
            if user.lower() in ('quit', 'exit'):
                break
            parts = user.split()
            if len(parts) != 3:
                print("Please enter three values separated by spaces.")
                continue
            x, y, z = parts
            message = f"{x},{y},{z}".encode('utf-8')
            client.sendall(message)
            data = client.recv(1024)
            print("Received response:", data.decode('utf-8'))
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print("Communication error:", e)
    finally:
        print("Closing connection...")
        client.close()



if __name__ == "__main__":
    main()