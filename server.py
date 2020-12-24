import socket
import threading
import time
import sys
import os
import codecs
import json
# TODO : fix cmd interpretation, move all cmd interpretation code to the client script
# TODO : write function for each command
# TODO : feature that allows user to send message to a specific user
#TODO : RUSSIFICATION
#! server doesn't parse commands, they come clearly defined  with the message

class Sender:  # class is responsible for sending messages to other users
    def __init__(self):
        self.encoding = "Windows 1251"
        self.max_header_size = 64

    def send_message(self, conn, msg):  # args : connection, user
        message_len = str(len(msg))
        message_len = self.to_byte_size(message_len)
        message_len_encoded = self.encode(msg)
        message_encoded = self.encode(msg)
        conn.send(message_len_encoded)
        conn.send(message_encoded)

    def encode(self, msg):
        msg = msg.encode(self.encoding)
        return msg

    def to_byte_size(self, msg):
        msg = msg+" "*(self.max_header_size-len(msg))
        print(len(msg))
        return msg

    # this function notifies sender that his message is on the server
    def notify_server_delivery(self):
        pass

    def notify_client_delivery(self):
        pass


class Parser:  # performs various operations on our messages
    def __init__(self):
        self.encoding = "Windows 1251"
        pass

    def encode(self, message):
        return message.encode(self.encoding)

    def decode(self, message):
        return message.decode(self.encoding)

    def json_to_obj(self, jsn):
        obj = json.loads(jsn)
        return obj

    def format_message_length(self, msg_len):
        msg_len = msg_len.decode(self.encoding)
        msg_len = msg_len.strip()
        msg_len = int(msg_len)
        return msg_len

    def decode_unwrap_message(self, msg):
        msg = self.decode(msg)
        msg = self.json_to_obj(msg)
        return msg


class Server:
    def __init__(self):
        self.HEADERSIZE = 64
        self.PORT = 5050
        self.IP = "192.168.1.191"  # changed for local for the time being
        self.ADDR = (self.IP, self.PORT)
        self.encoding = "utf-8"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.usercmds = {
            "-s:": "SEND_MESSAGE",
            # * these are functions that handle commands of clients, used in handle_client
            "-info:": self.sendInfo,
            "-disconnect:": self.disconnect_user,
        }
        # matrix, each element of array contains 3 vals
        self.connections = [["a"], ["b"], ["c"], ["d"], ["e"], ["f"]]
        # accountname, connection info #! if len of element == 1 -> account is free for use

    def sendInfo(self, conn):
        filepath = "info.txt"
        with codecs.open(filepath, "r", "Windows 1251") as file:
            info = file.read()
            info = info.encode("Windows 1251")
        conn.send(info)
        print(f"info was sent to {conn}")

    def disconnect_user(self, user):
        for i in range(len(self.connections)):
            if self.connections[i][0] == user:
                self.connections[i] = user

    def check_if_connected(self, indx):
        if len(self.connections[indx]) == 1:
            return False
        return True

    def add_to_connections(self, connection):  # returns index of our user in array
        for i in range(len(self.connections)):
            # if no user is not connected under this account
            if len(self.connections[i]) == 1:
                self.connections[i].append(connection)
                return i  # returns index of our user in array

    def handle_client(self, conn, addr):
        print(f"[New connection] {addr} connected")
        client_index = self.add_to_connections(conn)
        connected = True
        while self.check_if_connected(client_index):
            print(
                f"New connection {addr} has logged in as {self.connections[client_index][0]}")
            msg_length = conn.recv(self.HEADERSIZE)
            msg_length = parser.format_message_length(msg_length)
            message = conn.recv(msg_length)

            #! there must be a method decoding message
            unwrpt_message = parser.decode_unwrap_message()
            command = unwrpt_message["command"]

    def start(self):  # handles all connection and passes each connection for handle_client
        self.sock.bind(self.ADDR)
        self.sock.listen()
        print(f"[Listening] Server is listening on {self.IP}")
        while True:
            conn, addr = self.sock.accept()
            thread = threading.Thread(
                target=self.handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count()-1}")


parser = Parser()
server = Server()
print("Starting server")
server.start()


# code that is not needed as for now:

def exec_exit(self, *args):
    print("Shutting the server down")
    os._exit(0)
