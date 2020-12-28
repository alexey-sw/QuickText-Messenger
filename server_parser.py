import json


class Parser:  # performs various operations on our messages
    def __init__(self):
        self.encoding = "Windows 1251"
        self.max_header_len = 64

    def encode(self, message):
        return message.encode(self.encoding)

    def decode(self, message):
        return message.decode(self.encoding)

    def format_message_length(self, msg_len, to_client=True):  # msg - int
        if to_client:  # encoding our message_len
            msg_len = str(msg_len)
            msg_len = msg_len+" "*(self.max_header_len-len(msg_len))
            msg_len = self.encode(msg_len)
            return msg_len
        else:  # decoding our message_len
            msg_len = self.decode(msg_len)
            msg_len = int(msg_len.strip())
            return msg_len

    def json_to_obj(self, jsn):
        obj = json.loads(jsn)
        return obj

    def object_to_json(self, obj):
        json_string = json.dumps(obj)
        return json_string

    def format_message(self, msg, to_client=True):
        if to_client:
            msg = self.object_to_json(msg)
            msg = self.encode(msg)
            return msg
        else:
            msg = self.decode(msg)
            msg = self.json_to_obj(msg)
            return msg

