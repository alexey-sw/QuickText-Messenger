import socket
import threading
import time


#! commands available:
#? -info : information about the project
#? -s: send a message
#? -shtdwn: terminate server and end session


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
        msg_length = str(msg_length).encode(FORMAT)
        msg_length += b' '*(self.HEADERSIZE - len(msg_length))
        self.sock.send(msg_length)
        self.sock.send(message)
        response = self.sock.recv(2048)
        print(response)

#TODO: implement info command


client = Client()
client.start()
client.send("-s: Hello world")
client.send("-info:")
client.send("-hello:")
time.sleep(2)
client.send("-shtdwn:")
