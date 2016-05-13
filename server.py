import socket
import threading
from protocol import Connect
from protocol import Status
import protocol

bind_ip = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip, bind_port))
server.listen(5)

print("[*] Listening on %s:%d", (bind_ip, bind_port))

def handle_client(client_socket):

    #get request from client socket
    request = client_socket.recv(1024)
    print("[*] Recieved: %s", request)

    #turn plain-text request into packet w/ decode && print
    packet = protocol.decode(request)
    print("[*] Encoded Rebuilt packet", packet.encode())

    #resend the packet encoded() back
    client_socket.send(packet.encode())
    client_socket.close()

def handle_client_async(client_socket):
    while True:
        request = client_socket.recv(4096)
        if not request:
            pass
        else:
            packet = protocol.decode(request)
            print("[*] Encoded Rebuilt packet", packet.encode())
            if packet.opcode == Opcode.KEEP_ALIVE.__str__():
                client_socket.send(packet.encode())

    client_socket.close()


while True:
    client, addr = server.accept()
    print("[*] Accepted connection from %s:%d", (addr[0], addr[1]))

    client_handler = threading.Thread(target=handle_client,args=(client,))
    client_handler.start()
