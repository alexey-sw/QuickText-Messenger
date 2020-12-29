import threading
import colorama


class Cli:
    def __init__(self, client,parser):
        self.client = client
        self.parser = parser 
    def start(self):
        welc_message = "This is messenger developed by Alexey grishchenko"
        input_thread = threading.Thread(
            target=self.cli_interface, args=(welc_message,))
        input_thread.start()
    def print_server_message(self,message):#? object,arr<- -> None
        print(message["text"])
        return
     
    def print_error_message(self,message):#? object <- -> None 
        print(message["error"])
        return 
    
    def print_user_message(self,message):#? obj<- -> None | rework here!
        print(message["text"])
        return 
    
    def colorize_input(self,color):
        pass 
    
    def print_star(self,is_second = False): #? bool<- ->None 
        if is_second:
            print("*")
        else:
            print("*")
        return 
    
    def cli_interface(self, welc_message):#? string<- -> None 
        # print(welc_message)
        print("Started client ")
        while True:
            user_input = input()
            parsed_input = self.parser.parse_input(user_input)
            # check that text not an empty string
            if parsed_input and parsed_input["command"]:
                # updating recipient,delay of our message and so on
                self.client.update_message_state(parsed_input)

