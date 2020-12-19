import socket
import threading
import time
import sys
import os

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
TERMINATED = False
ADDR = (SERVER,PORT)
HEADER = 64 # each message contains this number of bytes coming before the message
# this info contains number bytesize of the main message
FORMAT = "utf-8"
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(ADDR)

def exec_exit():
    print("Shutting the server down")
    os._exit(0)
    
def parse_cmd(msg):
    cmd = msg[0:3]
    if cmd=="-ex":
        print("EXIT command received")
        return "EXIT"
    else:
        print("unknown command received")
        return None
        
    
    

def handle_client(conn,addr):
    global TERMINATED
    print(f"[New connection] {addr} connected")
    to_exit = False
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            cmd = parse_cmd(msg)
            if cmd == "EXIT":
                connected = False
                to_exit = True
            
            print(f"[{addr}] {msg}")
            conn.send(b"Msg received")
    
    conn.close()
    if to_exit:
        exec_exit()
        
def start(): #  handles all connection and passes each connection for handle_client
    server.listen()
    print(f"[Listening] Server is listening on {SERVER}")
    while True:
        conn,addr = server.accept()
        thread = threading.Thread(target = handle_client,args = (conn,addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count()-1}")
        
        
        

print("Starting server")
start()
