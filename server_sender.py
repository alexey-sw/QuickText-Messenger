import threading

#! rework error delivery 
class Sender:  # class is responsible for sending messages to other users
    def __init__(self,server,parser): #? class, class <- -> None
        self.encoding = "Windows 1251"
        self.max_header_size = 64
        self.server = server
        self.parser = parser

    def send_msg(self, msg):  #? obj<- -> None 
        recipient_account = msg["to"]
        delay = msg["delay"]
        msg_formatted = self.parser.format_message(msg, to_client=True)
        message_len = len(msg_formatted)
        message_len_formatted = self.parser.format_message_length(message_len, True)

        if delay:
            delay = float(delay)
            send_timer = threading.Timer(delay, self.send, args=(
                message_len_formatted, msg_formatted, recipient_account,True))
            send_timer.start()
        else:
            self.send(message_len_formatted, msg_formatted,
                      recipient_account,is_account = True)
        return  
       
    def send_server_msg(self,msg):#? obj<- -> None
        # no delays for this type of messages
        recipient_account = msg["to"]
        msg_formatted = self.parser.format_message(msg,to_client = True)
        msg_len = len(msg_formatted)
        msg_len_formatted = self.parser.format_message_length(msg_len,to_client = True)
        self.send(msg_len_formatted,msg_formatted,recipient_account,is_account = True)
        return 
    
    def send_client_deliv_notif(self,msg): #? obj <- -> None
        message_id = msg["id"]
        message = {
            "from":"SERVER",
            "to":msg["to"],
            "command":"-usr_deliv_success:",
            "time":self.server.get_time(),
            "text":"message has reached the client",
            "error":"",
            "id":message_id
        }
        self.send_server_msg(message)
        return None 
    
    def send_server_deliv_notif(self,msg): #? obj<- ->None
        # sends to sender that message was delivered 
        message_id = msg["id"]
        message = {
            "from":"SERVER",
            "to":msg["from"],
            "command":"-serv_deliv_success:",
            "time":self.server.get_time(),
            "text":"message has reached the server",
            "error":"",
            "id":message_id
        }
        self.send_server_msg(message)
        pass
    
    def send(self, msg_len_formatted, msg_formatted,addr, is_account): #? bytes, bytes, [string or arr], bool<- -> None
        if is_account == True:
            if self.server.is_online(addr):
                connection = self.get_conn(addr) # if account is passed as a param
            else:
                self.server.update_deliv_queue(msg_formatted)
                return 
        else:  # for beginning we will just ignore that message hasn't been sent to user if its
            # if connection is already in params 
            connection = addr
        connection.send(msg_len_formatted)
        connection.send(msg_formatted)
        return 

    def send_login_affirmation(self, account_name): # ? string<- -> None 
        print(f"Sending login affirmation to {account_name}")
        message = {
            "command": "-login_accept:",
            "time": self.server.get_time(),
            "from": "SERVER",
            "to": account_name,
            "error": "",
            "text":f"Successfully logged in as {account_name}"
        }

        self.send_server_msg(message)
        return

    # doesn't work because we don't have account value, if login is unsuccessfult
    def send_login_rejection(self, connection, error): #? arr, string <- -> None 
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
        self.send(message_len_formatted,message_formatted,connection,is_account=False)
        return
    def send_deliv_error(self,msg): #? object<- ->None
        response = {
            "command":"-usr_deliv_failure:",
            "time": self.server.get_time(),
            "from": "SERVER",
            "to":msg["from"],
            "error": "Such account doesn't exist", # the only reason why it can be 
            "delay": 0
        }
        self.send_server_msg(response)
        return 
    
    def get_conn(self, account_name): #? string <- -> [array, 0]
        for elem in self.server.connections:
            if elem[0] == account_name:
                if len(elem) != 1:  # if connection was specified

                    return elem[1]
                print(f"No account named '{account_name}' has been found!")
                return 0

        print(f"No account named '{account_name}' has been found!")
        return 0
    
    def send_account_status(self,message):
        account = message["text"]
        is_existent = self.server.is_existent(account)
        is_online = self.server.is_online(account) if is_existent else False
        message_obj = {
            "to":message["from"],
            "time":self.server.get_time(),
            "from":"SERVER",
            "error":"",
            "is_online":is_online,
            "is_existent":is_existent,
            "command":"-account_status:"
        }
        
        self.send_server_msg(message_obj)
        return 
