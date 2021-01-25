import socket
from sqlite3.dbapi2 import Date
import threading
import time
import os
import subprocess
from server_sender import Sender
from server_parser import Parser
from server_db import DB_Manager
from user_db import *

#! server doesn't parse commands, they come clearly defined  with the message


#! need to rework unread messages sending
# TODO: we don't have unsent messages anymore, all messages go to chat db

class Executor:
    def __init__(self, server):
        self.server = server
        self.user_db = server.user_db
        pass

    def execute(self, message):
        message_command = message["command"]
        if message_command == "-s:":
            # ! delay feature will be implemented here
            self.user_db.log_message(message)
            #! fix bug when user sends messages to himself
            sender.send_msg(message)
        elif message_command == "-delivery_confirmed:":
            print("delivery confirmed")
            sender.send_client_deliv_notif(message)
        elif message_command == "-check_status:":
            sender.send_account_status(message)
        elif message_command == "-display_chat:":
            self.server.send_chat_log(message)
        return None


class Server:
    def __init__(self):
        self.online_count = 0
        self.HEADERSIZE = 64
        self.PORT = 5050
        self.IP = "192.168.1.191"  # changed for local for the time being
        self.ADDR = (self.IP, self.PORT)
        self.encoding = "utf-8"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.status_commands = [
            "-delivery_confirmed:", "-d:", "-check_status:", "-display_chat:"]
        self.delivery_queue = []  # * list of objects whose messages have to be delivered
        self.db = DB_Manager()
        self.connections = []  # only currently available users
        self.user_db = User_db()
        self.cmd_executor = Executor(self)

    def get_time(self):  # ? ..<-   -> string
        return time.ctime()

    def disconnect_user(self, user_account):  # ? object<-  -> None
        for i in range(len(self.connections)):
            if self.connections[i][0] == user_account:
                del self.connections[i]
                break
        self.db.disconnect_user(user_account)
        # self.db.update_value(MAIN_TB, user_account, "is_online", 0)
        return None

    def login_client(self, conn):  # ? arr<-  ->array: [string,bool,string ]
        login_message_length = conn.recv(self.HEADERSIZE)

        login_message = conn.recv(parser.format_message_length(
            login_message_length, to_client=False))
        formatted_login_message = parser.format_message(login_message, False)
        account_name = formatted_login_message["text"]
        is_valid, error = self.account_validity_check(account_name)
        return [account_name, is_valid, error]

    def send_unread_messages(self, message_arr):  # ? arr of string  <- -> None
        print("sending unsent messages ")
        if message_arr:
            for message in message_arr:
                message = parser.json_to_obj(message)
                sender.send_msg(message)
        else:
            pass
        return

    def send_chat_log(self, message):  # ?(dict)->None
        account_to = message["from"]
        table_name = message["text"]
        message_array = self.user_db.retrive_messages(table_name)
        if message_array:
            for logged_message in message_array:
                print(logged_message)
                sender.send_log_msg(logged_message, account_to)
        else:
            print("No messages for chat: ", table_name)

        return None

    def process_unsent_messages(self, account):  # ? (string)->None
        unsent_messages = self.db.get_unsent_messages(account)
        print("sending these messages: ", unsent_messages, " to ", account)
        self.send_unread_messages(unsent_messages)
        self.db.delete_unsent_messages(account)
        return None

    def update_deliv_queue(self, message):  # ? bin<- -> return None
        # ! converting from bin to json
        message = parser.format_message(message, to_client=False)
        recipient_account = message["to"]
        print("updating deliv queue")
        date = message["time"]
        message = parser.object_to_json(message)
        self.db.update_unsent_messages(message, recipient_account, date)
        return None

    # returns index of our user in array
    def add_to_connections(self, connection, account_name):  # ? (obj,string)->None
        self.connections.append([account_name, connection])
        self.db.connect_user(account_name)
        # # self.db.update_value(MAIN_TB, account_name, "is_online", 1)
        return None

    def get_client_index(self, account_name):  # ? string<- ->int
        indx = list(map(lambda elem: elem[0], self.connections)).index(
            account_name)
        return indx

    def is_online(self, account_name):  # ? string<- -> bool
        ans = self.db.is_online(account_name)
        return ans

    # ? string<- ->array:[bool,string]
    def account_validity_check(self, account_name):
        if self.is_existent(account_name):
            # indx = self.get_client_index(account_name)
            if self.is_online(account_name):
                return [False, f"Account '{account_name}' is already in use"]
            else:
                return [True, ""]
        return [False, f"Account '{account_name}' doesn't exist"]

    def get_conn(self, account_name):  # ? (string) -> object
        for elem in self.connections:  # ! user cannot be offline
            if elem[0] == account_name:
                return elem[1]
        print(f"No account named '{account_name}' has been found!")
        return 0

    def is_existent(self, account_name):  # ? (string) -> bool
        ans = self.db.is_existent(account_name)
        return ans

    def handle_client(self, conn, addr):  # ? arr,string<-  -> None
        self.online_count += 1
        print(f"[New connection] {addr} connected")
        while True:
            account_name, is_valid, error = self.login_client(
                conn)  # error is "" if login was successful
            if is_valid:
                print(f"{addr} has been connected as {account_name}")
                self.add_to_connections(conn, account_name)
                sender.send_login_affirmation(account_name)
                break
            else:
                print(f"LoginProcessError: {error}")
                sender.send_login_rejection(conn, error)
                continue
        self.process_unsent_messages(account_name)
        self.db.get_tbl("MAIN_TABLE")
        while True:
            try:
                msg_length = conn.recv(self.HEADERSIZE)
            except:
                print(account_name, "disconnected")
                self.disconnect_user(account_name)
                self.db.get_tbl("MAIN_TABLE")
                if self.user_db.is_such_table("a|a"):
                    self.user_db.drop_tbl("a|a")
                print("line 181, table dropped")
                break
            msg_length = parser.format_message_length(msg_length, False)
            message = conn.recv(msg_length)

            unwrpt_message = parser.format_message(message, False)

            if unwrpt_message["command"] not in self.status_commands:
                sender.send_server_deliv_notif(unwrpt_message)
            self.cmd_executor.execute(unwrpt_message)

        return None

    def start_server_thread(self):
        while True:
            conn, addr = self.sock.accept()
            print(addr, "connected")
            user_thread = threading.Thread(
                target=self.handle_client, args=(conn, addr))
            user_thread.start()

   
    def start_command_prompt(self):
        def cmd_prompt():
            command = input(">")
            if command == "r":
                self.kill_server()
        prompt_thread = threading.Thread(target=cmd_prompt)
        prompt_thread.start()

    def start(self):  # ? ..<-  -> None
        self.sock.bind(self.ADDR)
        self.sock.listen()
        self.db.setup()
        self.user_db.setup()
        self.start_command_prompt()
        self.start_server_thread()

    def kill_server(self):
        os._exit(0)


parser = Parser()
server = Server()
sender = Sender(server, parser)
print("Starting server")
server.start()
