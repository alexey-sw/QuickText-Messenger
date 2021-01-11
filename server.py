import socket
from sqlite3.dbapi2 import Date
import threading
import time
import codecs
from server_sender import Sender
from server_parser import Parser
from server_db import DB_Manager
from queue import Queue
#! server doesn't parse commands, they come clearly defined  with the message
#TODO: implement multithreading with sqlite3

MAIN_TB = "MAIN_TABLE"
# server adds sql command to db.sql_queue 
# server sets flag 
# db manager updates everything 
# flag is set to false 
class Server:
    def __init__(self):
        self.online_count = 0
        self.HEADERSIZE = 64
        self.PORT = 5050
        self.IP = "192.168.1.191"  # changed for local for the time being
        self.ADDR = (self.IP, self.PORT)
        self.encoding = "utf-8"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # matrix, each element of array contains 3 vals
        # ! server identifies users using accountname, connection info #! if len of element == 1 -> account is free for use
        self.connections = [["a"], ["b"], ["c"], ["d"], ["e"], ["f"]]
        self.status_commands = ["-delivery_confirmed:", "-d:"]
        self.delivery_queue = []  # * list of objects whose messages have to be delivered
        self.db = DB_Manager()
        
    def get_time(self):  # ? ..<-   -> string
        return time.ctime()

    def disconnect_user(self, user_account):  # ? object<-  -> None
        for i in range(len(self.connections)):
            if self.connections[i][0] == user_account:
                print(f"'{user_account}' has been disconnected")
                self.connections[i] = [user_account]
                break
        self.db.update_value(MAIN_TB,user_account,"is_online",0)
        return
    
    def execute_client_command(self, message):  # ? object<- -> None
        message_command = message["command"]
        recipient_account = message["to"]
        delay = message["delay"] # if we want to append to message queue later 
        sender_account = message["from"]
        if message_command == "-s:":
            if self.is_existent(recipient_account):
                # we only need message_command, functions work with message_obj
                # if self.is_online(recipient_account):
                #     sender.send_msg(message) #! if user is online delay is handled by sender class 
                # else: #! otherwise it is handled by server method 
                #     append_timer = threading.Timer(delay,self.update_deliv_queue,(message,))
                #     append_timer.start()
                sender.send_msg(message)    
                    #! this will work out badly in case we have delay specified 
            else:
                sender.send_deliv_error(message) #! remove this shit 

        elif message_command == "-info:":
            pass
        elif message_command == "-delivery_confirmed:":
            sender.send_client_deliv_notif(message)
        elif message_command == "-check_status":
            sender.send_account_status(message)  
        return

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
                print(type(message))
                message = parser.json_to_obj(message)
                sender.send_msg(message)
        else:
            pass
        return

    def update_deliv_queue(self, message):  # ? bin<- -> return None
        message = parser.format_message(message,to_client = False)#! converting from bin to json   
        recipient_account = message["to"]
            
        print("updating deliv queu ")
        date = message["time"]
        message = parser.object_to_json(message)
        print(type(message))
        self.db.update_unsent_messages(message,recipient_account,date)
        self.db.get_tbl("UNREAD_MESSAGES")
        
            # self.delivery_queue.append([recipient_account, message])
            #! rewrite with db 
        return 
            

    # returns index of our user in array
    def add_to_connections(self, indx, connection,account_name):  # ? int,arr<- ->None
        self.connections[indx].append(connection)
        self.db.update_value(MAIN_TB,account_name,"is_online",1)
        return

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
            indx = self.get_client_index(account_name)
            if len(self.connections[indx]) != 1:
                print(self.connections[indx])
                return [False, f"Account '{account_name}' is already in use"]
            else:
                return [True, ""]
        return [False, f"Account '{account_name}' doesn't exist"]

    def is_existent(self, account_name): #! delete check_if_connected function 
        ans = self.db.is_existent(account_name)
        return ans 
    
    def handle_client(self, conn, addr):  # ? arr,string<-  -> None
        self.online_count += 1
        print(f"[New connection] {addr} connected")
        while True:
            account_name, is_valid, error = self.login_client(
                conn)  # error is "" if login was successful
            if is_valid:
                # it is easier to operate with client index
                client_index = self.get_client_index(account_name)
                # that with our account name
                self.add_to_connections(client_index, conn,account_name)
                print(f"{addr} has been connected as {account_name}")
                sender.send_login_affirmation(account_name)
                break
            else:
                print(f"LoginProcessError: {error}")
                sender.send_login_rejection(conn, error)
                continue
        
        unsent_messages = self.db.get_unsent_messages(account_name)
        print("sending these messages: ",unsent_messages," to ",account_name)
        self.send_unread_messages(unsent_messages)
        self.db.delete_unsent_messages(account_name)

        while True:
            try:
                
                msg_length = conn.recv(self.HEADERSIZE)
            
                msg_length = parser.format_message_length(msg_length, False)
                message = conn.recv(msg_length)

                unwrpt_message = parser.format_message(message, False)
               
                if unwrpt_message["command"] not in self.status_commands:
                    sender.send_server_deliv_notif(unwrpt_message)
                self.execute_client_command(unwrpt_message)
            except:
                print(account_name,"disconnected")
                self.disconnect_user(account_name)
                break
        return 
            
    def start_server_thread(self):
        while True:
            conn, addr = self.sock.accept()
            print(addr,"connected")
            user_thread = threading.Thread(
                target=self.handle_client, args=(conn, addr))
            user_thread.start()
            
    def start(self):  # ? ..<-  -> None
        self.sock.bind(self.ADDR)
        self.sock.listen()
        self.db.setup() 
        self.start_server_thread()


parser = Parser()
server = Server()
sender = Sender(server, parser)
print("Starting server")
server.start()
