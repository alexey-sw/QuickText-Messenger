import socket
import threading
import time
import json

#! commands available:
# ? -info : information about the project
# ? -s: send a message
# ? -shtdwn: terminate server and end session
class InputParser: # parses and composes message 
    def __init__(self):
        self.user_commands = ["-s:","-shtdwn:","-delay:","-switch:","-disconnect:"]
    def parse_input(self,user_input): #* wraps necessary properties of input in an object
        command = self.parse_cmd(user_input)
        text = self.cropMsg(user_input,command)
        time = self.get_time() #time of input 
        return {"text":text,"time":time,"command":command}
    
    def cropMsg(self,msg, cmd):
        cmdlen = len(cmd)
        msg = msg[cmdlen:]
        msg = msg.strip()
        return msg
    def get_time(self):
        return time.ctime()
    def parse_cmd(self,msg):
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
                if not cmd in self.user_commands:
                    raise CmdError
            except:
                print(f"Invalid command in message {msg}")
                return 0
            else:
                return cmd
    def object_to_json(self,object):
        pass
class Cli:
    def __init__(self,client):
        self.client = client
        
    def start(self):
        welc_message = "This is messenger developed by Alexey grishchenko"
        input_thread = threading.Thread(target=self.cli_interface,args =(welc_message))
        input_thread.start()
    
    
            
    def cli_interface(self,welc_message):
        print(welc_message)
        while True:
            user_input = input()
            parsed_input= InputParser.parse_input(user_input)
            if command:
                self.client.update_message_state() # updating recepient delay of our message and so on 
                
        
class Client:
    def __init__(self):

        self.SERVERPORT = 5050
        self.FORMAT = "utf-8"
        self.HEADERSIZE = 64
        self.SERVERIP = "192.168.1.191"
        self.SERVERADDR = (self.SERVERIP, self.SERVERPORT)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.to_send =False # flag that indicates whether we have to send message with current state 
        self.message_state = {
            "from":"someone",
            "to":"someone",
            "text":"",
            "time":"",
            "command":"",
            "delay":0
        }
        self.test_mode = True
    def start(self):
        if not self.test_mode:
            self.sock.connect(self.SERVERADDR)
            Cli = Cli(client)
            data_thread = threading.Thread(target = self.receive_data)
            data_thread.start()
    def receive_data(self): # data from server is passed in 2 parts : message_length and message itself
        #! client doesn't differentiate server messages from user messages
        
        pass
    
    def update_message_state(self): # updates message state and sends message
        
        
        
        if self.to_send==True:
            self.send(msg)

    def send(self,msg):
        msg
    # def receiveResponse(self):
    #     response = ""

    #     def exit_thread():
    #         nonlocal response
    #         if response:
    #             response = response.decode(encoding = "Windows 1251")
    #             print(f"Response from server: {response}\n\n")
    #         else:
    #             print("Unknown error,no response from server has been obtained, exiting thread")
    #     response_timer = threading.Timer(2.0,exit_thread)
    #     response_timer.start()
    #     response = self.sock.recv(1024)
        
    # def send(self, msg):  # variables in argument may change
    #     FORMAT = self.FORMAT
    #     command = self.parseCommand(msg)
    #     if command:
    #         msg = self.cropMsg(msg, command)
    #         msg = self.composeMessage(msg,command)
    #         message = msg.encode(FORMAT)
            
    #         msg_length = len(message)
    #         msg_length = str(msg_length).encode(FORMAT)

    #         msg_length += b' '*(self.HEADERSIZE - len(msg_length))
    #         self.sock.send(msg_length)
    #         self.sock.send(message)
    #         thread = threading.Thread(
    #             target=self.receiveResponse)
    #         thread.start()
            
    #         #TODO : receive response with a new thread
            
    #     else:
    #         pass # command was incorrect

client = Client()
client.start()