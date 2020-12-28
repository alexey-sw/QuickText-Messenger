import threading


class Sender:  # class is responsible for sending messages to other users
    def __init__(self,server,parser):
        self.encoding = "Windows 1251"
        self.max_header_size = 64
        self.server = server
        self.parser = parser

    def send_msg(self, msg):  # msg - message_object
        # we need to remove delay and to and not_notif_message properties from our message
        sender = msg["from"]
        recipient_account = msg["to"]
        delay = msg["delay"]
        msg_formatted = self.parser.format_message(msg, to_client=True)
        message_len = len(msg_formatted)
        message_len_formatted = self.parser.format_message_length(message_len, True)

        if delay:
            delay = float(delay)
            send_timer = threading.Timer(delay, self.send, args=(
                message_len_formatted, msg_formatted, recipient_account))
            send_timer.start()
        else:
            self.send(message_len_formatted, msg_formatted,
                      recipient_account)

    def send(self, msg_len_formatted, msg_formatted, recipient_account=None, connection=None):
        if connection == None:
            connection = self.get_conn(recipient_account)
        if connection:  # for beginning we will just ignore that message hasn't been sent to user if its
            # azzccount doesn't exist
            connection.send(msg_len_formatted)
            connection.send(msg_formatted)

    def send_login_affirmation(self, account_name):
        print(f"Sending login affirmation to {account_name}")
        message = {
            "command": "-login_accept:",
            "time": self.server.get_time(),
            "from": "SERVER",
            "to": account_name,
            "error": "",
            "delay": 0
        }

        self.send_msg(message)

    # doesn't work because we don't have account value, if login is unsuccessfult
    def send_login_rejection(self, connection, error):
        message = {
            "command": "-login_reject:",
            "time": self.server.get_time(),
            "from": "SERVER",
            "to":"unknown",
            "error": error,
            "delay": 0
            }
        message_formatted = self.parser.format_message(message,to_client=True)
        message_len = len(message_formatted)
        message_len_formatted = self.parser.format_message_length(message_len,to_client=True)
        print(message_len_formatted)
        self.send(message_len_formatted,message_formatted,recipient_account=None,connection = connection)

    def get_conn(self, account_name):
        for elem in self.server.connections:
            if elem[0] == account_name:
                if len(elem) != 1:  # if connection was specified

                    return elem[1]
                print(f"No account named '{account_name}' has been found!")
                return 0

        print(f"No account named '{account_name}' has been found!")
        return 0

    def send_info(self, account_name):
        pass
