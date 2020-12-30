import socket
import threading
import time
import json
import os
from client_parser import Parser
from gui import Gui,Main_Window



class Client:
    def __init__(self):
        self.SERVERPORT = 5050
        self.HEADERSIZE = 64
        self.SERVERIP = "192.168.1.191"
        self.SERVERADDR = (self.SERVERIP, self.SERVERPORT)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # flag that indicates whether we have to send message with current state
        self.to_send = False
        # self.user_commands = ["-s:", "-delay:", "-swtch:",
        #                       "-d:", "-delayall:"]  # for server from user , forgot about -info
        self.test_mode = False   # doesn't permit access to the Internet
        self.reset_delay = True
        self.account = "unknown"
        # commands that are not sent to server
        # self.setup_commands = ["-delay:", "-swtch:", "-delayall:"]
        self.help_string = "This is help string "  # * needs change
        self.logged_in = False
        self.gui = None 

    def start(self):
        if not self.test_mode:
            try:
                self.sock.connect(self.SERVERADDR)
            except:
                print("ServerError: try again later")
                self.exit_client()
            else:
                self.login_process(self.sock)
                data_thread = threading.Thread(
                    target=self.receive_data, args=(self.sock,))
                data_thread.start()
                gui = Gui(Main_Window,self)
                gui.start()
                

    def get_time(self):
        return time.ctime()
    
    def exit_client(self):
        os._exit(0)
        
    def is_from_server(self, msg):
        if msg["from"] == "SERVER":
            return True
        return False

    def receive_data(self, socket):
        # doesnt' receive messages from users 
        while True:
            message_len = socket.recv(64)
            formatted_msg_len = parser.format_message_length(
                message_len, False)
            message = socket.recv(formatted_msg_len)
            decoded_message = parser.format_message(message, to_server=False)
            is_server_message = self.is_from_server(decoded_message)
            print(decoded_message)
            if is_server_message:  # we don't send notifications for server messages
                self.execute_server_generated_commands(decoded_message)
            else:
                print(decoded_message)
                self.deliv_response(decoded_message)

    # one star near the message
    def execute_server_generated_commands(self, msg):  # ? obj<- -> None
        
        command = msg["command"]
        error = msg["error"]
        if error:
            print(msg)
        if command == "-login_accept:":
            self.logged_in = True
            obtained_account_val = msg["to"]
            self.account = obtained_account_val
        elif command == "-usr_deliv_success:" or command == "-serv_deliv_success:":
            if command == "-usr_deliv_success:":
                print("firststar")
            else:
                print("secondstar")
        elif command == "-account_status:":
            print("-account_status: " ,msg["text"])
        return

    def deliv_response(self, message):  # ? obj<- -> None
        sender = message["from"]
        response_message = {
            "from": self.account,
            "text": "",
            "to": sender,
            "time": self.get_time(),
            "command": "-delivery_confirmed:",
            "delay": 0
        }
        self.send_deliv_response(response_message)
        return

    def login_process(self, socket):  # ? -> None
        while not self.logged_in:
            account_name = input("Type name of your account: ")
            login_message_obj = {"text": account_name,  # ! if account_name is disconnect -> disconnect
                                 "from": "unknown",
                                 "delay": 0,
                                 "time": parser.get_time()
                                 }  # we create new message object not to change our global message state!
            login_message_formatted = parser.format_message(
                login_message_obj, to_server=True)
            message_len_formatted = parser.format_message_length(
                len(login_message_formatted), to_server=True)
            socket.send(message_len_formatted)
            socket.send(login_message_formatted)
            self.receive_login_response(socket)
        return
        # add field for password
    def receive_login_response(self, socket): 
        message_len = socket.recv(64)
        formatted_msg_len = parser.format_message_length(
            message_len, False)
        message = socket.recv(formatted_msg_len)
        decoded_message = parser.format_message(message, to_server=False)
        self.execute_server_generated_commands(decoded_message)
        return

    def send_message_obj(self,message):#? obj<- -> None 
        formatted_msg = parser.format_message(message,to_server = True)
        msg_len = len(formatted_msg)
        formatted_msg_len = parser.format_message_length(msg_len,to_server = True)
        self.send_bytes(formatted_msg_len)
        self.send_bytes(formatted_msg)
        return 
        
    def send_bytes(self, msg):  # ? bytes socket<-  -> None
        if not self.test_mode:
            try:
                self.sock.send(msg)
            except:
                print("ServerError: try again later")
        else:
            print(msg)
            
        return None 

    def send_deliv_response(self, msg):  # ? object <- -> None
        msg_formatted = parser.format_message(msg, to_server=True)
        msg_len_formatted = parser.format_message_length(
            len(msg_formatted), to_server=True)
        self.sock.send(msg_len_formatted)
        self.sock.send(msg_formatted)
        return


parser = Parser()
client = Client()
client.start()
