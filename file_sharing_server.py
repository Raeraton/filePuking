import socket
import my_file


file = my_file.RFile( input("enter file path: ") )



# network
SERVER_ADDR = ("0.0.0.0", 25665)
if input("not default ip? ") != "":
    SERVER_ADDR = ( input("ADDR: "), int(input("PORT: ")) )

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(SERVER_ADDR)



# getting clients
target_addr = None
packet_size = 0
while target_addr == None:
    try:

        print( f"waiting for client on {SERVER_ADDR[0]}:{SERVER_ADDR[1]}" )

        data, addr = sock.recvfrom( 64 )

        tokens = data.decode().split()
        if len(tokens) < 2:
            print( "wrong format recvd:", tokens )
            continue

        if tokens[0] != "connect":
            continue

        packet_size = int( tokens[1] )
        target_addr = addr

        sock.sendto( b"OK", target_addr )

    except Exception as e:
        print( "[ERROR]", e )

print( f"client connected {target_addr[0]}:{target_addr[1]}" )

sock.settimeout( 10 )
while 1:
    try:
    
        rcvd, addr = sock.recvfrom( 256 )
        if addr != target_addr:
            continue

        request = rcvd[:3]
        args = rcvd[3:]

        if request == b"RNG":

            start = int.from_bytes( args[:4], "big", signed=False )
            end = int.from_bytes( args[4:8], "big", signed=False )

            print( "rng", start, end )

            for i in range( start, end ):
                sock.sendto(
                    i.to_bytes(4,"big",signed=False) + file.get_bytes( i*packet_size, (i+1)*packet_size ),
                    target_addr
                )
            
        elif request == b"IDX":

            idxb = args[:4]
            idx = int.from_bytes(idxb,"big",signed=False)

            
            print( "idx", idx )
            
            sock.sendto( idxb + file.get_bytes( packet_size*idx, packet_size*(idx+1) ), target_addr )
            
        elif request == b"LEN":

            print( "len" )
            
            seq = args[:4]
            sock.sendto( seq + file.size.to_bytes(4,"big",signed=False), target_addr )

        elif request == b"END":
            print( "connection closed by client" )
            break


    except TimeoutError:
        print( "connection lost with target" )
        break
    except Exception as e:
        print( "[ERROR]", e )
        break