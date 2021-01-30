import threading

#! rework error delivery


class Sender:  # class is responsible for sending messages to other users
    def __init__(self, server, parser):  # ? class, class <- -> None
        self.encoding = "Windows 1251"
        self.max_header_size = 64
        self.server = server
        self.parser = parser

    def send_msg(self, msg):  # ? obj<- -> None
        sender = msg["from"]
        recipient_account = msg["to"]
        if sender == recipient_account:
            return None
        msg_formatted = self.parser.format_message(msg, to_client=True)
        message_len = len(msg_formatted)
        message_len_formatted = self.parser.format_message_length(
            message_len, True)
        self.send(message_len_formatted, msg_formatted,
                  recipient_account, is_account=True)
        return None

    def send_server_msg(self, msg):  # ? obj<- -> None
        # no delays for this type of messages
        recipient_account = msg["to"]
        msg_formatted = self.parser.format_message(msg, to_client=True)
        msg_len = len(msg_formatted)
        msg_len_formatted = self.parser.format_message_length(
            msg_len, to_client=True)
        self.send(msg_len_formatted, msg_formatted,
                  recipient_account, is_account=True)
        return None

    def send_client_deliv_notif(self, msg):  # ? obj <- -> None
        message_id = msg["id"]
        message = {
            "from": "SERVER",
            "to": msg["to"],
            "command": "-usr_deliv_success:",
            "time": self.server.get_time(),
            "text": msg["from"],
            "error": "",
            "id": message_id
        }
        self.send_server_msg(message)
        return None

    # ? bytes, bytes, [string or arr], bool<- -> None
    def send(self, msg_len_formatted, msg_formatted, addr, is_account):
        if is_account == True:  # if parameter specified is account
            if self.server.is_online(addr):
                connection = self.server.get_conn(addr)
            else:
                print("Client offline")
                return None
        else:  # for beginning we will just ignore that message hasn't been sent to user if its
            # if connection is already in params
            connection = addr
        connection.send(msg_len_formatted)
        connection.send(msg_formatted)
        return None

    def send_login_affirmation(self, account_name):  # ? string<- -> None
        print(f"Sending login affirmation to {account_name}")
        message = {
            "command": "-login_accept:",
            "time": self.server.get_time(),
            "from": "SERVER",
            "to": account_name,
            "error": "",
            "text": f"Successfully logged in as {account_name}"
        }

        self.send_server_msg(message)
        return None

    # doesn't work because we don't have account value, if login is unsuccessful
    def send_login_rejection(self, connection, error):  # ? arr, string <- -> None
        message = {
            "command": "-login_reject:",
            "time": self.server.get_time(),
            "from": "SERVER",
            "to": "unknown",
            "error": error,
            "delay": 0
        }
        message_formatted = self.parser.format_message(message, to_client=True)
        message_len = len(message_formatted)
        message_len_formatted = self.parser.format_message_length(
            message_len, to_client=True)
        self.send(message_len_formatted, message_formatted,
                  connection, is_account=False)
        return None

    def send_signup_affirmation(self,account_name):
        message = {
            "command": "-signup_accept:",
            "time": self.server.get_time(),
            "from": "SERVER",
            "to": account_name,
            "error": "",
            "text": f"Successfully logged in as {account_name}"
        }
        print("Sending signup affirmation ")
        self.send_server_msg(message)
        
        return None
    
    def send_signup_rejection(self,connection,error):#?(conn,string)->None 
        message = {
            "command": "-signup_reject:",
            "time": self.server.get_time(),
            "from": "SERVER",
            "to": "unknown",
            "error": error,
            "delay": 0
        }
        message_formatted = self.parser.format_message(message, to_client=True)
        message_len = len(message_formatted)
        message_len_formatted = self.parser.format_message_length(message_len, to_client=True)
        self.send(message_len_formatted, message_formatted , connection, is_account=False)
        return None 
    
    def convert_num(self, val):  # ?(int)->bool
        if val == 1:
            return True
        else:
            return False

    def send_log_msg(self, message, account):  # ?(arr)->None
        message_id = message[0]
        sender = message[1]
        text = message[2]
        date = message[3] #! rework 
        is_read = self.convert_num(message[4])
        message_obj = {
            "to": account,
            "from": "SERVER",
            "text": text,
            "id": message_id,
            "command": "-display_chat:",
            "is_read": is_read,
            "sender": sender,
            "error": ""
        }
        self.send_server_msg(message_obj)
        return None

    def send_account_status(self, message):
        account = message["text"]
        is_existent = self.server.is_existent(account)
        is_online = self.server.is_online(account) if is_existent else False
        message_obj = {
            "to": message["from"],
            "time": self.server.get_time(),
            "from": "SERVER",
            "error": "",
            "is_online": is_online,
            "is_existent": is_existent,
            "command": "-account_status:"
        }

        self.send_server_msg(message_obj)
        return None
