import socket
import threading
import protocol
from protocol import Opcode
from protocol import Status
from time import sleep

def keep_alive(socket):
    """ This function is used to ensure that both the client and the server are in fact connected."""
    client.send(protocol.Packet(Opcode.KEEP_ALIVE, Status.OK).encode())
    while True:
        request = socket.recv(4096)
        if(not request):
            pass
        else:
            packet = protocol.decode(request)
            print("[*] Encoded Rebuilt packet", packet.encode())
            if packet.opcode == protocol.Opcode.KEEP_ALIVE:
                sleep(2)
                socket.send(packet.encode())

target_host = '0.0.0.0'
target_port = 9999

x = protocol.Connect('lisa', {})

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((target_host,target_port))

client.send(x.encode())

response = client.recv(4096)

#handle connection response (if OK then start keep_alive thread)
print (protocol.decode(response).status)
if protocol.decode(response).status == protocol.Status.OK:
    keep_alive = threading.Thread(target=keep_alive, args=(client,))
    keep_alive.start()
