import socket
import my_file
import threading
import time


path = input( "enter out file path: " )
server_addr = (
    input("server addr: "),
    int(input("server port: "))
)
packet_size = input("enter packet size: ")
if packet_size == "": packet_size = 256
else: packet_size = int(packet_size)
range_size = int( input("enter range size: ") )

elfogyott_to = 0.1
if packet_size >= 2: elfogyott_to = float( input("to ~(0.01-1): ") )




#network
MY_ADDR = ("0.0.0.0", 0)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind( MY_ADDR )



print("connecting to server")
sock.settimeout(16)
sock.sendto( f"connect {packet_size}".encode(), server_addr )

while 1:
    data, addr = sock.recvfrom( 16 )
    if addr != server_addr: continue
    if data == b"OK": break
    raise RuntimeError("anyád szerver rossz válasz")


print( "connected to server" )
print( "getting filesize " )

file_size = 0
sock.settimeout(5)
sock.sendto( b"LEN####", server_addr )
while file_size == 0:
    try:

        data, addr = sock.recvfrom( 1024 )

        if addr != server_addr: continue
        if data[:4] != b"####": print( "wrong format", data )

        file_size = int.from_bytes( data[4:], "big", signed=False )

    except TimeoutError:
        sock.sendto( b"LEN####", server_addr )

print( "filesize is", file_size )
file = my_file.WFile( path, file_size )

packet_count = file_size // packet_size + (file_size%packet_size!=0)






packet_recved = 0
down_speed = 0
_update_network_stuff_running = True
def update_network_stuff():
    global packet_recved, down_speed, _update_network_stuff_running
    while _update_network_stuff_running:
        time.sleep(1)
        down_speed = packet_recved * packet_size * 8 / 1000000
        packet_recved = 0

update_network_stuff_thread = threading.Thread( target=update_network_stuff )
update_network_stuff_thread.start()




def recv_idx( i:int, sorted: bool ):
    global sock, packet_recved

    ib = i.to_bytes(4,"big",signed=False)
    sock.sendto(b"IDX" + ib, server_addr)
    while 1:
        try:
            data, addr = sock.recvfrom( packet_size + 32 )
                    
            if addr != server_addr: continue
    
            packet_idx = int.from_bytes( data[:4], "big", signed=False )
    
            if packet_idx != i:
                print( "wrong package recved", packet_idx,"!=",i )
                continue
    
            file.set_bytes( data[4:], i*packet_size )
            packet_recved += 1
            if sorted: print( f"{packet_count} / {i+1} recved    {down_speed} Mb/s" )
            else: print( f"recved: c {i}      {down_speed}Mb/s" )
            break
        except TimeoutError:
            sock.sendto(b"IDX" + ib, server_addr)



time_point = time.time()
if range_size < 2:

    print( "transfering one by one" )


    for i in range( packet_count ):
        recv_idx(i, True)

else:


    iterations = packet_count // range_size + (packet_count%range_size!=0)

    for i in range( iterations ):

        range_start = i * range_size
        range_end = min( range_start+range_size, packet_count )



        sock.sendto( 
            b"RNG" +
            range_start.to_bytes(4, "big", signed=False) + 
            range_end.to_bytes(4, "big", signed=False),
            server_addr
            )

        sock.settimeout(elfogyott_to) # TODO talalj ki valamit
        packet_left = range_size

        recved_packet_idxs = set()

        while packet_left > 0:
            try:
                
                data, addr = sock.recvfrom( packet_size + 32 )
                if addr != server_addr: continue

                packet_idx = int.from_bytes( data[:4], "big", signed=False )
                packet_cont = data[4:]
                packet_left -= 1
                packet_recved += 1

                recved_packet_idxs.add(packet_idx)

                print( f"recved:   {packet_idx}      {down_speed}Mb/s" )

                file.set_bytes( packet_cont, packet_idx*packet_size )

            except TimeoutError:
                for index in range(range_start, range_end):
                    if index not in recved_packet_idxs:
                        recv_idx(index, False)
                        packet_left -= 1
                break
print( f"completed or failed in {time.time()-time_point} sec" )





# cleanup
sock.sendto(b"END", server_addr)
sock.sendto(b"END", server_addr)
sock.sendto(b"END", server_addr)

_update_network_stuff_running = False
update_network_stuff_thread.join()