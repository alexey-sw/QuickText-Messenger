import time
import json


class Parser:  # parses and composes message, performs operations on messages
    def __init__(self):
        self.encoding = "Windows 1251"
        # forgot -last_online:  -help:
        self.max_header_len = 64  # max size of message_len in bytes

    # def parse_input(self, user_input):  # ? string< - -> [ obj or bool ]
    #     command = self.parse_cmd(user_input)
    #     text = self.cropMsg(user_input, command)
    #     time = self.get_time()  # time of input
    #     if self.delay_arg_correct(command, text):
    #         # delay and switch have their argument in text
    #         return {"text": text, "time": time, "command": command}
    #     return 0


    def encode(self, msg):  # ? string  <- -> bytes
        msg = msg.encode(self.encoding)
        return msg

    def decode(self, msg):  # ? bytes <- -> string
        msg = msg.decode(self.encoding)
        return msg

    def get_time(self):  # ? ..<- -> string
        return time.ctime()

    # def parse_cmd(self, msg):  # ? string<- -> string
    #     cmd = ""
    #     try:
    #         hyphen_index = msg.index("-")
    #         colon_index = msg.index(":")
    #     except ValueError:
    #         print(f"incorrect input: colon of hyphen missing in message {msg}")
    #         return ""
    #     else:
    #         for i in range(hyphen_index, colon_index+1):
    #             cmd = cmd + msg[i]
    #         try:
    #             if not cmd in self.user_commands:
    #                 raise CmdError
    #         except:
    #             print(f"Invalid command in message {msg}")
    #             return ""
    #         else:
    #             return cmd

    def object_to_json(self, obj):  # ? obj<- -> string
        json_string = json.dumps(obj)
        return json_string

    def json_to_obj(self, jsn):  # ? string<- -> object
        obj = json.loads(jsn)
        return obj

    # ? [int or bytes], bool<- -> [bytes or int]
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

    # ? [object or bytes], bool < - ->[bytes or object ]
    def format_message(self, msg, for_server=True):
        if for_server:
            msg = self.object_to_json(msg)
            msg = self.encode(msg)
            return msg
        else:
            msg = self.decode(msg)
            msg = self.json_to_obj(msg)
            return msg
