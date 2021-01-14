# User db will have n tables 
# each table represents a chat : current_user - some user 

# each row represents new message 
#? columns: MESSAGE_ID(int autoincrement) MESSAGE(text) DATE(string) IS_DELIVERED(bool) IS_READ(bool) 
#! we don't read value IS_DELIVERED and IS_READ if message has been sent from another account 
#! message column contains plaintext only 

#Algorithm:
# anytime user click select:
# if value is different 
# we look for table  CHAT_WITH_(ACCOUNT_NAME)
# if there is no such table we create one 
# if there is such table, then we retrieve all messages and append them to scrollArea and mark them according to IS_DELIVERED and IS_READ flag
import sqlite3
import time
DEFAULT_TABLE = "sqlite_sequence"

#! there will be high level function upload_to_table(message)

class User_db:
    def __init__(self,filedir):#? (string)->None  
        self.connection = sqlite3.connect(filedir)
        self.to_drop = True 
        self.db_dir = filedir
    
    def setup(self):#? ()-> None 
        try:
            
            if self.to_drop:
                for table in self.get_all_tbl():
                    if table!=DEFAULT_TABLE:
                        print(table)
                        self.drop_tbl(table)                
        except:
            print("error occured on line 38") 
            
        table_name = "CHAT_WITH_b" if self.db_dir == "usrA.db" else "CHAT_WITH_a"
        self.create_table(table_name)
        self.connection.commit()
        return None 
    
    def get_all_tbl(self): #?()->[of string]
        cursor = self.connection.cursor()
        table_array =cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        self.connection.commit()
        table_array = list(map(lambda elem:elem[0],table_array))
        
        return table_array
    
    #* edit operations 
    def add_to_table(self,message):#?(string,dict)->None
        account_from = message["from"]
        table_name = self.compose_table_name(account_from)
        cursor = self.connection.cursor()
        date = message["time"]
        text = message["text"]
        message_id = message["id"]
        cursor.execute("""INSERT INTO {}
            (
                MESSAGE_ID,
                MESSAGE_TEXT,
                DATE,
                IS_DELIVERED ,
                IS_READ
                ) VALUES(?,?,?,?,?)""".format(table_name),(message_id,text,date,0,0))
        self.connection.commit()
        return None 

    def retrive_messages(self,table):#?(string)->[[id(INT),text(string),date(string),IS_DELIVERED(bool),IS_READ(bool)]] 
        cursor = self.connection.cursor()
        message_matrix = cursor.execute("""SELECT * FROM {}""".format(table)).fetchall()
        return message_matrix
    
    def compose_table_name(self,account_name):#? (string)->string 
        table_string = f"CHAT_WITH_{account_name}"
        return table_string
    
    def print_tbl(self,table):#? (string)->None
        cursor = self.connection.cursor()
        for row in cursor.execute('''SELECT * FROM {}'''.format(table)):
            print(row)
        
        return None 
    
    def create_table(self,table_name):#?(string) ->Bool
        cursor = self.connection.cursor()
        cursor.execute("""CREATE TABLE {}(
            MESSAGE_ID INTEGER PRIMARY KEY,
            MESSAGE_TEXT TEXT,
            DATE TEXT,
            IS_DELIVERED INTEGER,
            IS_READ INTEGER
            );
            """.format(table_name))
        self.connection.commit()
        return None 
    
    def drop_tbl(self,table):#?(string)->None 
        cursor = self.connection.cursor()
        cursor.execute("DROP TABLE {};".format(table))
        self.connection.commit()
        return None 
        
    def is_such_table(self,table):#? (string) -> Bool
        table_array =self.get_all_tbl()
        if table in table_array:
            return True 
        else:
            return False
    
    
        # user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        #                         account_name TEXT,
        #                         is_online INTEGER

def get_time():
    return time.ctime()

db = User_db("usrA.db")
db.setup()
table_name = "CHAT_WITH_b"
for i in range(100):
    response_message = {
            "from":"b",
            "text": "",
            "to": "salam_aleikum",
            "time": get_time(),
            "command": "-delivery_confirmed:",
            "delay": 0,
            "id":i
        }
    db.add_to_table(response_message)
print(db.retrive_messages(table_name))