import socket
import threading
import time


class Client:
    def __init__(self):

        self.SERVERPORT = 5050
        self.FORMAT = "utf-8"
        self.HEADERSIZE = 64
        self.IP = socket.gethostbyname(socket.gethostname())
        self.SERVERADDR = (self.IP, self.SERVERPORT)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.sock.connect(self.SERVERADDR)

    def send(self, msg):  # variables in argument may change
        FORMAT = self.FORMAT
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' '*(self.HEADERSIZE - len(send_length))
        self.sock.send(send_length)
        self.sock.send(message)
        response = self.sock.recv(2048)
        print(response)
# objective: send commands to server in json format


client = Client()
client.start()
client.send("-s: Hello world")
time.sleep(2)
client.send("-ex:")
