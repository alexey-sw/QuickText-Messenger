import socket
import threading
import time
import json
import os
#! thoughts for the future : we need to keep track of all sent messages
#! it might be useful to store our messages and their sending time in some structure

# TODO : send messages to multiple users


class Parser:  # parses and composes message, performs operations on messages
    def __init__(self):
        self.user_commands = ["-s:", "-delay:", "-switch:",
                              "-disconnect:", "-delayall:"]  # for server, forgot about -info
        self.encoding = "Windows 1251"
        # forgot -last_online:  -help:
        self.setup_commands = ["-delay:", "-switch:", "-delayall:"]
        self.max_header_len = 64  # max size of message_len in bytes

    def parse_input(self, user_input):  # * wraps necessary properties of input in an object
        command = self.parse_cmd(user_input)
        text = self.cropMsg(user_input, command)
        time = self.get_time()  # time of input
        if self.delay_arg_correct(command, text):
            # delay and switch have their argument in text
            return {"text": text, "time": time, "command": command}
        return 0

    def delay_arg_correct(self, command, text):
        if command == "-delay:" or command == "-delayall:":
            try:
                text = int(text)
            except:
                print(f"Invalid argument for {command} function: {text}")
                return False
            else:
                return True
        else:
            return True  # if it is not delay command automatically return true

    def encode(self, msg):
        msg = msg.encode(self.encoding)
        return msg

    def decode(self, msg):
        msg = msg.decode(self.encoding)
        return msg

    def cropMsg(self, msg, cmd):
        cmdlen = len(cmd)
        msg = msg[cmdlen:]
        msg = msg.strip()
        return msg

    def get_time(self):
        return time.ctime()

    def parse_cmd(self, msg):
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

    def object_to_json(self, obj):
        json_string = json.dumps(obj)
        return json_string

    def json_to_obj(self, jsn):
        obj = json.loads(jsn)
        return obj

    def add_to_maxlen(self, msg_len):
        msg_len = msg_len+" "*(self-len(msg_len))

    def format_message_length(self, msg_len, for_server=True):
        if for_server:  # encoding our message_len
            msg_len = str(msg_len)
            msg_len = msg_len+" "*(self.max_header_len-len(msg_len))
            msg_len = self.encode(msg_len)
            return msg_len
        else:  # decoding our message_len
            msg_len = self.decode(msg_len)
            msg_len = int(msg_len.strip())
            return msg_len

    def format_message(self, msg, for_server=True):
        if for_server:
            msg = self.object_to_json(msg)
            msg = self.encode(msg)
            return msg
        else:
            msg = self.decode(msg)
            msg = self.json_to_obj(msg)
            return msg


class Cli:
    def __init__(self, client):
        self.client = client

    def start(self):
        welc_message = "This is messenger developed by Alexey grishchenko"
        input_thread = threading.Thread(
            target=self.cli_interface, args=(welc_message,))
        input_thread.start()

    def cli_interface(self, welc_message):
        print(welc_message)
        while True:
            user_input = input()
            parsed_input = parser.parse_input(user_input)
            # check that text not an empty string
            if parsed_input and parsed_input["command"]:
                # updating recipient,delay of our message and so on
                self.client.update_message_state(parsed_input)


class Client:
    def __init__(self):

        self.SERVERPORT = 5050
        self.HEADERSIZE = 64
        self.SERVERIP = "192.168.1.191"
        self.SERVERADDR = (self.SERVERIP, self.SERVERPORT)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # flag that indicates whether we have to send message with current state
        self.to_send = False
        self.message_state = {
            "from": "a",
            "to": "a",
            "text": "",
            "time": "",
            "command": "",
            "delay": 0,
            # flag that indicates whether message should be resent or audited by server
            "not_notif_message": True  # if message is generated by user
        }
        self.test_mode = False  # doesn't permit access to the Internet
        self.reset_delay = True
        # commands that are not sent to server
        self.setup_commands = ["-delay:", "-switch:", "-delayall:"]
        self.help_string = "This is help string "  # * needs change

    def exit_client(self):
        os._exit(0)

    def start(self):
        global Cli
        
        if not self.test_mode:
            try:
                self.sock.connect(self.SERVERADDR)
            except:
                print("ServerError: try again later")
                self.exit_client()
            else:
                self.login_process(self.sock)
                Cli = Cli(client)
                Cli.start()
                data_thread = threading.Thread(
                    target=self.receive_data, args=(self.sock,))
                data_thread.start()
    # data from server is passed in 2 parts : message_length and message itself
    # there will be 3 types of messages: user messages, error messages and delivered messages

    def receive_data(self, socket):
        #! client doesn't differentiate server messages from user messages
        while True:
            message_len = socket.recv(64)
            formatted_msg_len = parser.format_message_length(
                message_len, False)
            message = socket.recv(formatted_msg_len)
            decoded_message = parser.decode(message)
            print("Message from server: ", decoded_message, "\n\n")

    def response_from_server(self):  # one star near the message
        pass

    def response_from_client(self):  # two stars near the message
        pass

    def login_process(self, socket):
        while True:
            account_name = input("Type name of your account: ")
            login_message_obj = {"text":account_name, #! if account_name is disconnect -> disconnect: 
                                "from":"unknown",
                                "delay": 0,
                                "not_notif_message": True,
                                "time": parser.get_time()
                                }  # we create new message object not to change our global message state!
            login_message_formatted = parser.format_message(
                login_message_obj, for_server=True) 
            message_len_formatted = parser.format_message_length(
                len(login_message_formatted), for_server = True)
            socket.send(message_len_formatted)
            socket.send(login_message_formatted)

        # add field for password

    def change_message_property(self, name, value):
        self.message_state[name] = value

    def update(self, update):

        if update["command"] not in self.setup_commands:
            self.to_send = True  # sending immediately if not delay or switch comamnd
            if update["command"] == "-disconnect:":
                exit_timer = threading.Timer(2.0, self.exit_client)
                exit_timer.start()
                self.change_message_property("not_notif_message", True)
                # !need to clean message state # except from, time, not notif
            if update["command"] == "-s:":
                self.change_message_property("not_notif_message", True)
                self.change_message_property("text", update["text"])
            self.change_message_property("command", update["command"])
            self.change_message_property("time", update["time"])

        # don't consider time for delay and switch commands
        elif update["command"] == "-delay:":
            # we don't delay disconnect messages
            self.reset_delay = True
            self.change_message_property("delay", int(update["text"]))

        elif update["command"] == "-switch:":
            self.change_message_property("to", update["text"])

        elif update["command"] == "-delayall:":
            self.reset_delay = False
            self.change_message_property("delay", update["text"])

    # updates message state and sends message

    def update_message_state(self, msg):
        self.update(msg)  # updates message state
        # print(self.message_state, " message obj") # for testing
        if self.to_send == True:  # if send flag is true
            self.to_send = False
            raw_message = self.message_state
            json_message = parser.object_to_json(raw_message)
            formatted_msg_len = parser.format_message_length(len(json_message))
            encoded_message = parser.encode(json_message)
            if self.reset_delay == True:
                self.change_message_property("delay", 0)
            self.send(formatted_msg_len, self.sock)
            self.send(encoded_message, self.sock)
            # reset delay

    def send(self, msg, socket):
        if not self.test_mode:
            try:
                socket.send(msg)
            except:
                print("ServerError: try again later")
        else:
            print(msg)


parser = Parser()
client = Client()
client.start()
