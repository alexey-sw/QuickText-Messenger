from encryption import Encryptor,Decryptor,Key_Message

#key manager must be able to work with existing db 


class Key_Manager:
    def __init__(self):
        self.db_dir = "key_db.db"
        self.to_drop = False

    
    def set_key(self,table):
        pass
    
    
    def retrieve_key(self,table):
        pass
    
    
    
