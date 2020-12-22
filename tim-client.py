import socket
import threading
import time
import json

#! commands available:
# ? -info : information about the project
# ? -s: send a message
# ? -shtdwn: terminate server and end session


class Client:
    def __init__(self):

        self.SERVERPORT = 5050
        self.FORMAT = "utf-8"
        self.HEADERSIZE = 64
        self.SERVERIP = socket.gethostbyname(socket.gethostname())
        print(self.SERVERIP)
        self.SERVERADDR = (self.SERVERIP, self.SERVERPORT)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.usercmds = {
            "-s:":"SEND_MESSAGE",
            "-shtdwn:":"SHUTDOWN", #* these are functions that handle commands of clients, used in handle_client
            "-info:":"SHOW_INFO"
            
        }

    def start(self):
        self.sock.connect(self.SERVERADDR)
    
    def parseCommand(self,msg):
        cmd = ""
        try:
            hyphen_index = msg.index("-")
            colon_index = msg.index(":")
        except ValueError:
            print(f"incorrect input: colon of hyphen missing in message {msg}")
            return 0
        else:
            for i in range(hyphen_index, colon_index+1):
                cmd = cmd + msg[i]
            try:  
                if not cmd in self.usercmds:
                    raise CmdError
            except:
                print(f"Invalid command in message {msg}")
                return 0
            else:
                return cmd
            
    def composeMessage(self,msg,command): # converts message into json format
        composed_message = {
            "from":socket.gethostbyname(socket.gethostname()),
            "to":"Vasya",
            "time":time.time(),
            "text":msg,
            "cmd":command
        }
        json_composed_message = json.dumps(composed_message)
        return json_composed_message        
    
    def cropMsg(self,msg, cmd):
        cmdlen = len(cmd)
        msg = msg[cmdlen:]
        return msg

    def send(self, msg):  # variables in argument may change
        FORMAT = self.FORMAT
        command = self.parseCommand(msg)
        if command:
            msg = self.cropMsg(msg, command)
            msg = self.composeMessage(msg,command)
            message = msg.encode(FORMAT)
            
            msg_length = len(message)
            msg_length = str(msg_length).encode(FORMAT)

            msg_length += b' '*(self.HEADERSIZE - len(msg_length))
            self.sock.send(msg_length)
            self.sock.send(message)
            response = self.sock.recv(1024)
            print(response.decode(encoding="Windows 1251"))
        else:
            pass # command was incorrect
        
        #! there was a problem with sending all messages due to the fact that client was awaiting server response
        #! need to work on it with threading


client = Client()
client.start()
client.send("-info:wtf")