import socket
import time

path = input( "file path:" )
server_addr = (
    input( "server ip:" ),
    int( input("server port:") )
)

BLOCK_SIZE = 65536
bs = input( "block size (or nothing):" )
if bs != "":
    BLOCK_SIZE = int(bs)



sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect( server_addr )

print( "connected to server" )

sock.sendall(f"gimmi {BLOCK_SIZE}\n".encode())

print( "block size sent" )

time_when_started = time.time()
with open(path, "wb") as file:
    time_point = 0
    recved_bytes = 0
    all_recv_bytes = 0

    while 1:
        data = sock.recv(BLOCK_SIZE)
        if not data: break
        file.write(data)

        recved_bytes += len(data)
        all_recv_bytes += len(data)
        tn = time.time()
        if tn - time_point >= 1:
            time_point = tn
            print( f"{all_recv_bytes/(1024**2)} MB\t     downspeed: {recved_bytes*8/1000000} Mb/s" )
            recved_bytes = 0

        
print( f"file recved in {time.time() - time_when_started} s" )