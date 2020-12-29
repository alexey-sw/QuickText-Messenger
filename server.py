import socket
import threading
import time
import codecs
from server_sender import Sender
from server_parser import Parser

#! server doesn't parse commands, they come clearly defined  with the message

# TODO: implement delivery confirmation
# TODO: notification that user is offline and message wasn't sent
# TODO: implement programm for message_delivery_failure


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
        self.status_commands = ["-delivery_confirmed:", "-disconnect:"]
        self.delivery_queue = []  # * list of objects whose messages have to be delivered

    def get_time(self):  # ? ..<-   -> string
        return time.ctime()

    def sendInfo(self, conn):  # doesn't work!
        filepath = "info.txt"
        with codecs.open(filepath, "r", "Windows 1251") as file:
            info = file.read()
            info = info.encode("Windows 1251")
        conn.send(info)
        print(f"info was sent to {conn}")

    def disconnect_user(self, msg):  # ? object<-  -> None
        user_to_disconnect = msg["from"]
        for i in range(len(self.connections)):
            if self.connections[i][0] == user_to_disconnect:
                print(f"'{user_to_disconnect}' has been disconnected")
                self.connections[i] = [user_to_disconnect]
                print(self.connections, " - connections\n")
                break
        return

    def execute_client_command(self, message):  # ? object<- -> None
        message_command = message["command"]
        recipient_account = message["to"]
        print(recipient_account)
        if message_command == "-s:":
            if self.is_existent(recipient_account):
                # we only need message_command, functions work with message_obj
                if self.is_online(recipient_account):
                    sender.send_msg(message)
                else:
                    self.update_deliv_queue(message)
            else:
                sender.send_deliv_error(message)

        elif message_command == "-info:":
            pass

        elif message_command == "-disconnect:":
            self.disconnect_user(message)

        elif message_command == "-delivery_confirmed:":
            sender.send_client_deliv_notif(message)
        return

    def check_if_connected(self, account_name):  # ? int<- -> bool
        for elem in self.connections:
            if elem[0]==account_name:
                return True 
        return False 

    def login_client(self, conn):  # ? arr<-  ->array: [string,bool,string ]
        login_message_length = conn.recv(self.HEADERSIZE)

        login_message = conn.recv(parser.format_message_length(
            login_message_length, to_client=False))
        formatted_login_message = parser.format_message(login_message, False)
        account_name = formatted_login_message["text"]
        if account_name == "-disconnect:":
            # !need to work here
            pass
        is_valid, error = self.account_validity_check(account_name)

        return [account_name, is_valid, error]

    def has_unread_messages(self, account_name):  # ? string<- -> bool
        for elem in self.delivery_queue:
            if elem[0] == account_name:
                return True

        print(f"no messages for {account_name}")
        return False

    def get_unread_messages(self, account_name):  # ? string<- ->array
        message_arr = []
        for elem in self.delivery_queue:
            if elem[0] == account_name:
                message_arr.append(elem[1])
        return message_arr

    def send_unread_messages(self, message_arr):  # ? arr of obj  <- -> None
        for message in message_arr:
            sender.send_msg(message)
        return

    def update_deliv_queue(self, message):  # ? obj<- -> return None
        recipient_account = message["to"]
        self.delivery_queue.append([recipient_account, message])

    # returns index of our user in array
    def add_to_connections(self, indx, connection):  # ? int,arr<- ->None
        self.connections[indx].append(connection)
        return

    def get_client_index(self, account_name):  # ? string<- ->int
        indx = list(map(lambda elem: elem[0], self.connections)).index(
            account_name)
        return indx

    def is_online(self, account_name):  # ? string<- -> bool
        for elem in self.connections:
            if elem[0] == account_name:
                if len(elem) == 2:
                    return True
                else:
                    return False

    # ? string<- ->array:[bool,string]
    def account_validity_check(self, account_name):
        account_names = list(map(lambda elem: elem[0], self.connections))
        if account_name in account_names:
            indx = self.get_client_index(account_name)
            if len(self.connections[indx]) != 1:
                return [False, "this account is already in use"]
            else:
                return [True, ""]
        return [False, "this account doesn't exist"]

    def is_existent(self, account_name):
        account_names = list(map(lambda elem: elem[0], self.connections))
        if account_name in account_names:
            return True
        else:
            return False

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
                self.add_to_connections(client_index, conn)
                print(f"{addr} has been connected as {account_name}")
                sender.send_login_affirmation(account_name)
                break
            else:
                print(f"LoginProcessError: {error}")
                sender.send_login_rejection(conn, error)
                continue

        if self.has_unread_messages(account_name):
            unread_messages = self.get_unread_messages(account_name)
            self.send_unread_messages(unread_messages)

        while self.check_if_connected(account_name):
            try:
                msg_length = conn.recv(self.HEADERSIZE)
            except:
                print(
                    f"{account_name} disconnected from the server")
                break
            msg_length = parser.format_message_length(msg_length, False)
            message = conn.recv(msg_length)

            unwrpt_message = parser.format_message(message, False)
            # need to rewrite it for failure_delivery
            if unwrpt_message["command"] not in self.status_commands:
                sender.send_server_deliv_notif(unwrpt_message)
            self.execute_client_command(unwrpt_message)
        return

    def start(self):  # ? ..<-  -> None
        self.sock.bind(self.ADDR)
        self.sock.listen()
        print(f"[Listening] Server is listening on {self.IP}")
        while True:
            conn, addr = self.sock.accept()
            thread = threading.Thread(
                target=self.handle_client, args=(conn, addr))
            thread.start()
        


parser = Parser()
server = Server()
sender = Sender(server, parser)
print("Starting server")
server.start()
