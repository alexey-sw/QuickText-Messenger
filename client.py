import socket
import threading
import time
import json

class Parser:  # parses and composes message
    def __init__(self):
        self.user_commands = ["-s:", "-delay:", "-switch:",
                              "-disconnect:", "-delayall:"]  # for server
        self.encoding = "Windows 1251"
        self.setup_commands = ["-delay:", "-switch:", "-delayall:"]

    def parse_input(self, user_input):  # * wraps necessary properties of input in an object
        command = self.parse_cmd(user_input)
        text = self.cropMsg(user_input, command)
        time = self.get_time()  # time of input
        if self.delay_arg_correct(command,text):
        # delay and switch have their argument in text
            return {"text": text, "time": time, "command": command}
        return 0
    
    def delay_arg_correct(self,command,text):
        if command == "-delay:" or command == "-delayall:":
            try:
                text = int(text)
            except:
                print(f"Invalid argument for {command} function: {text}")
                return False
            else:
                return True
        else:
            return True # if it is not delay command automatically return true 
            
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
            parsed_input = Parser.parse_input(user_input)
            if parsed_input and parsed_input["command"] :# check that text not an empty string
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
            "from": "someone",
            "to": "someone",
            "text": "",
            "time": "",
            "command": "",
            "delay": 0,
            # flag that indicates whether message should be resent or audited by server
            "is_message": True
        }
        self.test_mode = True
        self.reset_delay = True
        # commands that are not sent to server
        self.setup_commands = ["-delay:", "-switch:", "-delayall:"]

    def start(self):
        global Cli
        Cli = Cli(client)
        Cli.start()
        if not self.test_mode:
            self.sock.connect(self.SERVERADDR)
            data_thread = threading.Thread(
                target=self.receive_data, args=(self.sock,))
            data_thread.start()

    # data from server is passed in 2 parts : message_length and message itself
    def receive_data(self, socket): # there will be 3 types of messages: user messages, error messages and delivered messages
        #! client doesn't differentiate server messages from user messages
        while True:
            message_len = socket.recv(64)
            message = socket.recv(message_len)
            decoded_message = Parser.decode(message)
            print("Message from server: ", decoded_message, "\n\n")

    def response_from_server(self):
        pass
    
    def response_from_client(self):
        pass
    
    def change_property(self, name, value):
        self.message_state[name] = value

    def update(self, update):

        if update["command"] not in self.setup_commands:
            self.to_send = True  # sending immediately if not delay or switch comamnd
            if update["command"] == "-disconnect:":
                self.change_property("is_message", False)
            if update["command"] == "-s:":
                self.change_property("is_message", True)
            self.change_property("command", update["command"])
            self.change_property("time", update["time"])

        # don't consider time for delay and switch commands
        elif update["command"] == "-delay:":
            # we don't delay disconnect messages
            self.reset_delay = True
            self.change_property("delay", update["text"])

        elif update["command"] == "-switch:":
            self.change_property("to", update["text"])

        elif update["command"] == "-delayall:":
            self.reset_delay = False
            self.change_property("delay", update["text"])

    # updates message state and sends message

    def update_message_state(self, msg):
        self.update(msg)  # updates message state
        print(self.message_state, " message obj")
        if self.to_send == True:  # if send flag is true
            print(True)
            self.to_send = False

            raw_message = self.message_state
            json_message = Parser.object_to_json(raw_message)
            encoded_message = Parser.encode(json_message)
            if self.reset_delay == True:
                print("here")
                self.change_property("delay", 0)
            self.send(encoded_message, self.sock)
            # reset delay

    def send(self, msg, socket):
        print(msg, " message_string")
    
Parser = Parser()
client = Client()
client.start()
