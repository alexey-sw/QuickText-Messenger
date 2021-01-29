import socket
from threading import Timer,Thread
import time
import json
import os
from client_parser import Parser
from gui import Gui, Main_Window


class Client:
    def __init__(self):
        self.SERVERPORT = 5050
        self.HEADERSIZE = 64
        self.SERVERIP = "localhost"
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
        self.messages_to_display = []  # this will be a database query
        self.chat_account_status = {
            "account": None,  # none if account doesn't exist
            "is_existent": None,
            "is_online": None,
            "status_checked": None  # None is used when we are in the process
            # status_checked is the main flag: None if we are in process, false if values have been obtained but gui hasn't
            # displayed info yet, true if gui has displayed the value
        }
        self.delivered_messages = []  # texts of delivered messages

    def start(self):  # ? ()->None
        if not self.test_mode:
            try:
                self.sock.connect(self.SERVERADDR)
            except:
                print("ServerError: try again later")
                self.exit_client()
            else:
                self.login_process(self.sock)
                data_thread = Thread(
                    target=self.receive_data, args=(self.sock,))
                data_thread.start()
                # need to launch gui code in the same thread
                self.gui = Gui(Main_Window, self, self.messages_to_display)
                self.gui.start()

    def get_time(self):  # ? ()->string
        return time.ctime()

    def exit_client(self):  # ? ()->string
        os._exit(0)

    def is_from_server(self, msg):  # ? (dict)->bool
        if msg["from"] == "SERVER":
            return True
        return False

    def receive_data(self, socket):  # ? (obj)->None
        while True:
            try:
                message_len = socket.recv(64)
            except:
                print("client error")
                break
            formatted_msg_len = parser.format_message_length(
                message_len, False)
            message = socket.recv(formatted_msg_len)
            decoded_message = parser.format_message(
                message, to_server=False)
            is_server_message = self.is_from_server(decoded_message)
            if is_server_message:  # we don't send notifications for server messages
                self.execute_server_generated_commands(decoded_message)
                print(decoded_message, "-message received")
            else:
                print(decoded_message, "-message received")
                self.display_message(decoded_message)
                self.deliv_response(decoded_message)
        self.exit_client()

    def display_message(self, decoded_message):  # ?(dict)->None
        if "sender" in decoded_message.keys():
            param = "sender"
            print("sender param")
        else:
            param = "from"
        val = decoded_message[param]
        if val == self.chat_account_status["account"] or val == self.account:
            text = decoded_message["text"]
            status_vals = self.get_status_values(decoded_message)
            self.messages_to_display.append([text, status_vals])
            return None
        else:
            print("Message irrelevant")
            return None

    def get_status_values(self, decoded_message):
        key_arr = decoded_message.keys()
        sender = decoded_message["sender"] if "sender" in key_arr else decoded_message["from"]
        from_this_account = True if sender == self.account else False
        if from_this_account:
            is_read = decoded_message["is_read"]
            return [from_this_account, is_read]
        else:
            return [from_this_account]

    def execute_server_generated_commands(self, msg):  # ? (obj)->None
        command = msg["command"]
        error = msg["error"]
        if error:
            print(msg)
        if command == "-login_accept:":
            self.logged_in = True
            obtained_account_val = msg["to"]
            self.account = obtained_account_val
        elif command == "-display_chat:":
            print("to display message")
            self.display_message(msg)
        elif command == "-usr_deliv_success:":
            
            message_id = msg["id"]
            sender = msg["text"]
            print("delivery response from user: ",sender )
            if sender == self.chat_account_status["account"]:
                self.gui.highlight_message(message_id)

        elif command == "-account_status:":
            self.update_chat_account_status(msg)
        return None

    def is_this_account(self, account):
        if account == self.account:
            return True
        else:
            return False

    def deliv_response(self, message):  # ? (obj)->None
        print("message delivered")
        sender = message["from"]
        print(sender,message["from"]," sender, messagefrom")
        if sender != self.chat_account_status["account"]:
            print("sender!=self.chat_account_status")
            return None
        message_id = message["id"]
        response_message = {
            "from": self.account,
            "text": "",
            "to": sender,
            "time": self.get_time(),
            "command": "-delivery_confirmed:",
            "delay": 0,
            "id": message_id
        }
        print("sending deliv response to ",sender)
        self.send_deliv_response(response_message)
        return None

    def login_process(self, socket):  # ?(obj) -> None
        while not self.logged_in:
            account_name = input("Type name of your account: ")
            login_message_obj = {"text": account_name,  # ! if account_name is disconnect -> disconnect
                                 "from": "unknown",
                                 "delay": 0,
                                 "time": parser.get_time(),
                                 "to": "SERVER"
                                 }  # we create new message object not to change our global message state!
            login_message_formatted = parser.format_message(
                login_message_obj, to_server=True)
            message_len_formatted = parser.format_message_length(
                len(login_message_formatted), to_server=True)
            socket.send(message_len_formatted)
            socket.send(login_message_formatted)
            self.receive_login_response(socket)
        return None
        # add field for password

    def receive_login_response(self, socket):
        message_len = socket.recv(64)
        formatted_msg_len = parser.format_message_length(
            message_len, False)
        message = socket.recv(formatted_msg_len)
        decoded_message = parser.format_message(message, to_server=False)
        self.execute_server_generated_commands(decoded_message)
        return None

    def get_chat_string(self):
        account_arr = [self.account, self.chat_account_status["account"]]
        account_arr.sort()
        account_string = f"[{account_arr[0]}|{account_arr[1]}]"
        return account_string

    def display_chat(self):
        chat_string = self.get_chat_string()
        message_obj = {
            "text": chat_string,  # ! if account_name is disconnect -> disconnect
            "from": self.account,
            "delay": 0,
            "time": parser.get_time(),
            "to": "SERVER",
            "command": "-display_chat:"
        }
        self.send_message_obj(message_obj)
        return None

    def send_message_obj(self, message):  # ? obj<- -> None
        formatted_msg = parser.format_message(message, to_server=True)
        msg_len = len(formatted_msg)
        formatted_msg_len = parser.format_message_length(
            msg_len, to_server=True)
        self.send_bytes(formatted_msg_len)
        self.send_bytes(formatted_msg)
        return None

    def get_account_status(self, account):
        self.chat_account_status["account"] = account
        self.chat_account_status["status_checked"] = None
        message_obj = {
            "text": account,  # ! if account_name is disconnect -> disconnect
            "from": self.account,
            "delay": 0,
            "time": parser.get_time(),
            "to": "SERVER",
            "command": "-check_status:"
        }
        self.send_message_obj(message_obj)
        return None

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
        msg_len_formatted = parser.format_message_length(len(msg_formatted), to_server=True)
        self.sock.send(msg_len_formatted)
        self.sock.send(msg_formatted)
        return None

    def update_chat_account_status(self, message):
        self.chat_account_status["is_existent"] = message["is_existent"]
        self.chat_account_status["is_online"] = message["is_online"]
        if not message["is_existent"]:
            self.chat_account_status["is_existent"] = None
        self.chat_account_status["status_checked"] = False
        return None


parser = Parser()
client = Client()
client.start()
