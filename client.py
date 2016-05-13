import socket
import protocol

target_host = '0.0.0.0'
target_port = 9999

x = protocol.Connect('lisa', {})

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((target_host,target_port))

client.send(x.encode())


response = client.recv(4096)

#handle connection response (if OK then start keep_alive)



print (protocol.decode(response).status)
