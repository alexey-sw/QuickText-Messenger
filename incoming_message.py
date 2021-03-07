
class Incoming_Message:
    def __init__(self, dictionary,client_account):
        self.date = None
        self.text = None
        self.from_this_account =None
        self.is_read = None
        self.sender = None 
        self.id = None 
        
        self.setup(dictionary,client_account)

    def setup(self, dictionary,client_account):
        param = "sender" if "sender" in dictionary.keys() else "from"
        val = dictionary[param]
        self.sender = val
        self.text = dictionary["text"]
        self.id = dictionary["id"]
        # self.date = dictionary["time"]
        self.set_status_values(dictionary,client_account)
        return None 
    
    def set_status_values(self, dictionary,client_account):
        self.from_this_account = True if client_account==self.sender else False
        
        if not(self.from_this_account):
            self.is_read = dictionary["is_read"]
        else:
            self.is_read = True #! if we sent message to ourselves,then we have already read it 
 
            
        return None
