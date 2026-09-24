import socket
import threading

file_path = input("file path: ")

SERVER_ADDR = ("0.0.0.0", 25665)

if input("not default ip? ") != "":
    SERVER_ADDR = (
        input("ADDR: "),
        int(input("PORT: "))
    )

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(SERVER_ADDR)
sock.listen(5)

print(f"listening on {SERVER_ADDR[0]}:{SERVER_ADDR[1]}")


def handle_client(s: socket.socket, a):


    print(f"connected {a[0]}:{a[1]}")

    try:
        # Receive request until newline
        data = b""

        while b"\n" not in data:
            chunk = s.recv(1024)

            if not chunk:
                return

            data += chunk

        data = data.decode().strip()
        parts = data.split()

        if not parts or parts[0] != "gimmi":
            return

        block_size = 65536

        if len(parts) >= 2:
            block_size = int(parts[1])

        print(f"{a[0]}:{a[1]} using {block_size} sized blocks")

        with open(file_path, "rb") as file:
            while True:
                data = file.read(block_size)

                if not data:
                    break

                s.sendall(data)

    except Exception as e:
        print("[ERROR]", e)

    finally:
        s.close()

    print(f"disconnected {a[0]}:{a[1]}")


ths = []

try:
    while True:
        s, a = sock.accept()

        th = threading.Thread(
            target=handle_client,
            args=(s, a)
        )

        th.start()
        ths.append(th)

except KeyboardInterrupt:
    print("shutting down...")

finally:
    sock.close()

    for th in ths:
        th.join()