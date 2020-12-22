import socket
import threading
import time
import sys
import os
import codecs
import json
#TODO : fix cmd interpretation, move all cmd interpretation code to the client script 
#TODO : write function for each command 
#TODO : feature that allows user to send message to a specific user 
#TODO : RUSSIFICATION
#! server doesn't parse commands, they come clearly defined  with the message
class Server:
    def __init__(self):
        self.HEADERSIZE = 64
        self.PORT = 5050
        self.IP = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.IP, self.PORT)
        self.FORMAT = "utf-8"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.usercmds = {
            "-s:":"SEND_MESSAGE",
            "-shtdwn:":self.exec_exit, #* these are functions that handle commands of clients, used in handle_client
            "-info:":self.sendInfo
            
        }
        
    def exec_exit(self,*args):
        print("Shutting the server down")
        os._exit(0)
        
    def sendInfo(self,conn):
        filepath = "info.txt"
        with codecs.open(filepath,"r","Windows 1251") as file:
            info = file.read()
            info = info.encode("Windows 1251")
        conn.send(info)
        print(f"info was sent to {conn}")
        
    def parse_cmd(self, msg):
        message_dict = json.loads(msg)
        print(message_dict)
        return message_dict["cmd"]
    
    def handle_client(self, conn, addr):
        print(f"[New connection] {addr} connected")
        to_exit = False
        connected = True
        while connected:
            msg_length = conn.recv(self.HEADERSIZE).decode(self.FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(self.FORMAT)
                #! there must be a method decoding message
                cmd = self.parse_cmd(msg)
                
                if self.usercmds[cmd]=="SEND_MESSAGE":
                    print("SEND_MESSAGE command")
                    print(f"[{addr}] has sent message: {msg}")
                    conn.send(b"Msg received")
                else:
                    self.usercmds[cmd](conn)
    

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
