import socket
from threading import Timer, Thread
import time
import os
from server_sender import Sender
from server_parser import Parser
from server_db import DB_Manager
from user_db import *
# Todo: rework status alternation


class Executor:
    def __init__(self, server):
        self.server = server
        self.user_db = server.user_db
        pass

    def execute(self, message):
        message_command = message["command"]
        if message_command == "-s:":
            self.server.process_message(message)
        elif message_command == "-delivery_confirmed:":
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
        self.IP = "localhost"  # changed for local for the time being
        self.ADDR = (self.IP, self.PORT)
        self.encoding = "utf-8"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        return None
    def get_user_name(self,connection):
        for elem in self.connections:
            if elem[1] == connection:
                return elem[0]
            
    # ? arr<-  ->array: [string,bool,string ]
    def get_login_status(self, conn):
        try:
            login_message_length = conn.recv(self.HEADERSIZE)
        except:
            print("sign-in process has been aborted")
            return ["",False,"aborted"] 
        login_message = conn.recv(parser.format_message_length(
            login_message_length, to_client=False))
        formatted_login_message = parser.format_message(login_message, False)
        account_name = formatted_login_message["text"]
        is_valid, error = self.account_validity_check(account_name)
        return [account_name, is_valid, error]

    def get_signup_status(self, conn):
        try:
            signup_message_length = conn.recv(self.HEADERSIZE)
        except:
            print("sign-up process has been aborted")
            return ["",False,"aborted"] 
        
        signup_message = conn.recv(parser.format_message_length(
            signup_message_length, to_client=False))
        formatted_signup_message = parser.format_message(signup_message, False)
        account_name = formatted_signup_message["text"]
        if self.is_existent(account_name):
            is_valid = False
            error = "Such account already exists"
            return [account_name, is_valid, error]
        else:
            error = ""
            is_valid = True
            return [account_name, is_valid, error]

    def process_message(self, message):
        delay = float(message["delay"])
        log_timer = Timer(delay, self.user_db.log_message, args=(message,))
        message_timer = Timer(delay, sender.send_msg, args=(message,))
        log_timer.start()
        message_timer.start()
        return None

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

    def start_login_loop(self, conn, addr):
        while True:
            account_name, is_valid, error = self.get_login_status(
                conn)  # error is "" if login was successful
            if is_valid:
                print(f"{addr} has been connected as {account_name}")
                self.add_to_connections(conn, account_name)
                sender.send_login_affirmation(account_name)
                return account_name
            else:
                print(f"LoginProcessError: {error}")
                if error =="aborted":
                    return None 
                sender.send_login_rejection(conn, error)
                continue

    def start_signup_loop(self, conn, addr):  # ? (conn,addr)->string
        #! in this loop all we need to do is to check that account doesn't exist
        # * if account exists when signup was successful
        while True:
            account_name, is_valid, error = self.get_signup_status(conn)
            if is_valid == False:
                print("Singup failed for ", account_name)
                if error == "aborted":
                    return None 
                sender.send_signup_rejection(conn, error)
                continue
            else:
                print("Signup successful for ", account_name)
                self.add_to_connections(conn, account_name)
                self.db.append_client(account_name)
                sender.send_signup_affirmation(account_name)
                return account_name

    def get_authorisation_message(self, conn, addr):
        try:
            msg_length = conn.recv(self.HEADERSIZE)
        except:
            print("authorisation failed for addr :", addr)
            return None
        msg_length = parser.format_message_length(msg_length, False)
        message = conn.recv(msg_length)
        unwrpt_message = parser.format_message(message, False)
        print(unwrpt_message)
        return unwrpt_message

    def handle_client(self, conn, addr):  # ? arr,string<-  -> None
        self.online_count += 1
        print(f"[New connection] {addr} connected")
        message = self.get_authorisation_message(conn, addr)
        if message == None:  # * authorisation failed
            return None
        if message["command"] == "-sign_in:":
            account_name = self.start_login_loop(conn, addr)
        else:
            account_name = self.start_signup_loop(conn, addr)
        if account_name == None:
            print("Session aborted")
            return None 
        
        self.db.get_tbl("MAIN_TABLE")
        while True:
            try:
                msg_length = conn.recv(self.HEADERSIZE)
            except:
                print(account_name, "disconnected")
                self.disconnect_user(account_name)
                self.db.get_tbl("MAIN_TABLE")
                break
            msg_length = parser.format_message_length(msg_length, False)
            message = conn.recv(msg_length)
            unwrpt_message = parser.format_message(message, False)
            self.cmd_executor.execute(unwrpt_message)

        return None

    def get_user_list(self):
        user_list = list(map(lambda x: x[0], self.connections))
        return user_list

    def start_server_thread(self):
        while True:
            conn, addr = self.sock.accept()
            print(addr, "connected")
            user_thread = Thread(
                target=self.handle_client, args=(conn, addr))
            user_thread.start()

    def process_cli_command(self, command):

        # Todo : drop and recreate table instead of deleting all the contents
        if command == "r":
            self.db.disconnect_all()
            self.kill_server()
        elif command == "clrmsg":
            self.user_db.delete_messages()
        elif command == "clrusr":
            self.db.delete_users()
            self.user_db.delete_messages()
        else:
            print(" Undefined command : {}".format(command))

        return None

    def start_command_prompt(self):

        def cmd_prompt():
            while True:

                command = input(">")
                self.process_cli_command(command)

        prompt_thread = Thread(target=cmd_prompt)
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
