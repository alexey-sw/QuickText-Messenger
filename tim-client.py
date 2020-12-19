import socket
import threading
import time



PORT = 5050
FORMAT = "utf-8"
HEADER = 64
DISCONNECT_MESSAGE = "!Disconnect"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER,PORT)

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(ADDR)



def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' '*(HEADER  - len(send_length))
    client.send(send_length)
    client.send(message)
    response = client.recv(2048)
    print(response)
# objective: send commands to server in json format 


send("-s: Hello world")
time.sleep(2)
send("-ex:")
# trial : -s message  server prints message on its side
# -ex whatever I write : stop server


    