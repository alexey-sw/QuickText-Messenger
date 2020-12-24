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
        self.user_commands = ["-s:","-delay:","-switch:","-disconnect:"]# for server
        self.encoding = "Windows 1251"
    def parse_input(self,user_input): #* wraps necessary properties of input in an object
        command = self.parse_cmd(user_input)
        text = self.cropMsg(user_input,command)
        time = self.get_time() #time of input 
        return {"text":text,"time":time,"command":command} # delay and switch have their argument in text 
    
    def encode(self,msg):
        msg = msg.encode(self.encoding)
        return msg
    
    def decode(self,msg):
        msg = msg.decode(self.encoding)
        return msg
    
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
            return ""
        else:
            for i in range(hyphen_index, colon_index+1):
                cmd = cmd + msg[i]
            try:  
                if not cmd in self.user_commands:
                    raise CmdError
            except:
                print(f"Invalid command in message {msg}")
                return ""
            else:
                return cmd
            
    def object_to_json(self,obj):
        json_string = json.dumps(obj)
        return json_string
    
class Cli:
    def __init__(self,client):
        self.client = client
        
    def start(self):
        welc_message = "This is messenger developed by Alexey grishchenko"
        input_thread = threading.Thread(target=self.cli_interface,args =(welc_message,))
        input_thread.start()
    
    
            
    def cli_interface(self,welc_message):
        print(welc_message)
        while True:
            user_input = input()
            parsed_input= InputParser.parse_input(user_input)
            if parsed_input["command"]:
                self.client.update_message_state(parsed_input) # updating recipient,delay of our message and so on 
                
        
class Client:
    def __init__(self):

        self.SERVERPORT = 5050
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
            "delay":0,
            "is_message":True # flag that indicates whether message should be resent or audited by server
        }
        self.test_mode = True
    def start(self):
        global Cli
        Cli = Cli(client)
        Cli.start()
        if not self.test_mode:
            self.sock.connect(self.SERVERADDR)
            data_thread = threading.Thread(target = self.receive_data,args = (self.sock,))
            data_thread.start()
            
    def receive_data(self,socket): # data from server is passed in 2 parts : message_length and message itself
        #! client doesn't differentiate server messages from user messages
        while True:
            message_len = socket.recv(64)
            message = socket.recv(message_len)
            decoded_message = InputParser.decode(message)
            print("Message from server: ",decoded_message,"\n\n")
    def change_property(self,name,value):
        self.message_state[name]=value
    def update(self,update):
        
        if update["command"] !="-delay:" and update["command"]!="-switch:":
            self.to_send==True # sending immediately if not delay or switch comamnd
            if update["command"]=="-disconnect:":
                self.change_property("is_message",False)
            if update["command"]=="-s:":
                self.change_property("is_message",True)
            self.change_property("command",update["command"])
            self.change_property("time",update["time"])   

        elif update["command"]=="-delay:":
            self.change_property("delay",update["text"])
        elif update["command"] =="-switch:":
            self.change_property("to",update["text"])
            
    def update_message_state(self,msg): # updates message state and sends message
        self.update(msg)
        if self.to_send==True: # if send flag is true
            self.to_send = False
            raw_message = self.message_state
            json_message = InputParser.object_to_json(raw_message)
            encoded_message = InputParser.encode(json_message)
            self.send(msg,self.sock)
            #reset delay

    def send(self,msg,socket):
        print(msg)
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
InputParser = InputParser()
client = Client()
client.start()