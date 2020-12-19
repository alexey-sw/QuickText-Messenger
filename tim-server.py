import socket
import threading
import time
import sys
import os

# PORT = 5050
# SERVER = socket.gethostbyname(socket.gethostname())
# TERMINATED = False
# ADDR = (SERVER,PORT)
# HEADERSIZE = 64 # each message contains this number of bytes coming before the message
# # this info contains number bytesize of the main message
# FORMAT = "utf-8"
# server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# server.bind(ADDR)


class Server:
    def __init__(self):
        self.HEADERSIZE = 64
        self.PORT = 5050
        self.IP = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.IP, self.PORT)
        self.FORMAT = "utf-8"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def exec_exit(self):
        print("Shutting the server down")
        os._exit(0)

    def parse_cmd(self, msg):
        cmd = msg[0:3]
        if cmd == "-ex":
            print("EXIT command received")
            return "EXIT"
        else:
            print("unknown command received")
            return None

    def handle_client(self, conn, addr):
        print(f"[New connection] {addr} connected")
        to_exit = False
        connected = True
        while connected:
            msg_length = conn.recv(self.HEADERSIZE).decode(self.FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(self.FORMAT)
                cmd = self.parse_cmd(msg)
                if cmd == "EXIT":
                    connected = False
                    to_exit = True

                print(f"[{addr}] {msg}")
                conn.send(b"Msg received")

        conn.close()
        if to_exit:
            self.exec_exit()

    def start(self):  # handles all connection and passes each connection for handle_client
        self.sock.bind(self.ADDR)
        self.sock.listen()
        print(f"[Listening] Server is listening on {self.IP}")
        while True:
            conn, addr = self.sock.accept()
            thread = threading.Thread(
                target=self.handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count()-1}")


server = Server()
print("Starting server")
server.start()
