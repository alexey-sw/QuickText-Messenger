import sqlite3
from encryption import *
#! import statement     
#key manager must be able to work with existing db 


class Key_Manager:
    def __init__(self):
        self.db_dir = "key_db.db"
        self.connection = sqlite3.connect(self.db_dir,check_same_thread=False)
        self.to_drop = False

    
    def setup(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute("""CREATE TABLE ENCRYPTION_KEYS
                           (
                                KEY_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                CHAT TEXT,
                                KEY TEXT
                            )""")
        except:
            print("Table with encryption keys has already been created")
        self.connection.commit()
        del cursor 
        return None 
    
    
    def set_key(self,chat):#? (string)->None
        """ Sets unique key for every chat """
        cursor = self.connection.cursor()
        key = generate_key()
        cursor.execute('INSERT INTO ENCRYPTION_KEYS(CHAT,KEY) VALUES (?,?)', (chat,key ))
        self.connection.commit()
        del cursor 
        return None 
    
    def delete_keys(self):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM ENCRYPTION_KEYS")
        self.connection.commit()
        del cursor
        return None 
    
    
    def retrieve_key(self,table):#? (string)-> string 
        cursor = self.connection.cursor()
        key = cursor.execute("SELECT KEY FROM ENCRYPTION_KEYS WHERE CHAT = (?)",(table,)).fetchall()
        print(key)
        key = key[0]
        self.connection.commit()
        del cursor 
        return key  
    
    
# km = Key_Manager()
# km.setup()
# km.set_key("[a|b]")
# km.retrieve_key("[a|b]")