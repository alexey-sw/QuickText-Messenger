# User db will have n tables 
# each table represents a chat : current_user - some user 

# each row represents new message 
#? columns: MESSAGE_ID(int autoincrement) MESSAGE(text) DATE(string) IS_DELIVERED(bool) IS_READ(bool) 
#! we don't read value IS_DELIVERED and IS_READ if message has been sent from another account 
#! message column contains plaintext only 

#Algorithm for chat change:
# anytime user click select:
# if value is different 
# we look for table  CHAT_WITH_(ACCOUNT_NAME)
# if there is no such table we create one 
# if there is such table, then we retrieve all messages and append them to scrollArea and mark them according to IS_DELIVERED and IS_READ flag

#Algorithm for message delivery:
#if message is delivered from client -> check that select value is the same 
#if select value is the same : display message, write message into db, 
# otherwise write message into db

#if message is from server-> change message status 


#! user will not be able to log in under the same account on different devices 
import sqlite3
import time
#! fix it 
DEFAULT_TABLE = "sqlite_sequence"

#Todo: change message status when message is read, remove unsent messages 
class User_db:
    def __init__(self):#? (string)->None  
        self.db_dir = "user_db.db"
        self.connection = sqlite3.connect(self.db_dir,check_same_thread=False)
        self.to_drop = True 
    
    def setup(self):#? ()-> None 
        print(self.get_all_tbl())
        if self.to_drop:
            for table in self.get_all_tbl():
                if table!=DEFAULT_TABLE:
                    self.drop_tbl(table)                

        return None 
    
    def get_all_tbl(self): #?()->[of string]
        cursor = self.connection.cursor()
        table_array =cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        self.connection.commit()
        table_array = list(map(lambda elem:"["+elem[0]+"]",table_array))
        return table_array
    
    
    
    #* edit operations 
    def log_message(self,message):#?(string,dict)->None
        account_from = message["from"]
        account_to = message["to"]
        table_name = self.compose_table_name(account_from,account_to)
        print("All tables", self.get_all_tbl())
        print(table_name,"table name")
        if not(self.is_such_table(table_name)):
            self.create_table(table_name)
        cursor = self.connection.cursor()
        date = message["time"]
        text = message["text"]
        message_id = message["id"]
        is_delivered = 0
        is_read = 0
        if account_from == account_to:
            is_delivered = 1
            is_read = 1  
        print("appended message to table: ",table_name)
        #! unique constraint failed! 
        cursor.execute("""INSERT INTO {}
            (
                MESSAGE_ID,
                SENDER,
                MESSAGE_TEXT,
                DATE,
                IS_DELIVERED ,
                IS_READ
                ) VALUES(?,?,?,?,?,?)""".format(table_name),(message_id,account_from,text,date,is_delivered,is_read))
        self.connection.commit()
        print(self.retrive_messages(table_name))
        return None 

    def retrive_messages(self,table):#?(string)->[[id(INT),text(string),date(string),IS_DELIVERED(bool),IS_READ(bool)]] 
        cursor = self.connection.cursor()
        if self.is_such_table(table):
            message_matrix = cursor.execute("""SELECT * FROM {}""".format(table)).fetchall()
            return message_matrix
        else:
            return None 
    
    def compose_table_name(self,first_account,second_account):#? (string)->string 
        account_array = [first_account,second_account]
        account_array.sort()
        table_string = f"[{account_array[0]}|{account_array[1]}]"
        print(table_string)
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
            SENDER TEXT,
            MESSAGE_TEXT TEXT,
            DATE TEXT,
            IS_DELIVERED INTEGER,
            IS_READ INTEGER
            );
            """.format(table_name))
        self.connection.commit()
        return None 
    
    def drop_tbl(self,table):#?(string)->None
        table = self.correct_table_spelling(table)
        cursor = self.connection.cursor()
        cursor.execute("DROP TABLE {};".format(table))
        self.connection.commit()
        return None 
    
    def correct_table_spelling(self,table_name):#?(string)->string
        if not "["  or not "]" in table_name:
            table_name = f"[{table_name}]"
        else:
            pass
        return table_name
    
            

    def is_such_table(self,table):#? (string) -> Bool
        if not "[" or  not "]" in table:
            print(table,"tablename line 130")
            table = f"[{table}]"
        print(table,"tablename line 132")

        table_array =self.get_all_tbl()
        if table in table_array:
            return True 
        else:
            return False
    
    def register_user_pair(self,account_1,account_2):
        table_name = self.compose_table_name(account_1,account_2)
        self.create_table(table_name)
        return None 
    
    
    
        
def get_time():
    return time.ctime()
# if __name__=="__main__":
#     db = User_db()
#     db.setup()
#     alph = "abcdefghigklmnopqrstuvwxyz"
#     for i in range(20):
#         response_message = {
#                 "from":alph[1],
#                 "text": "",
#                 "to": alph[4],
#                 "time": get_time(),
#                 "command": "-delivery_confirmed:",
#                 "delay": 0,
#                 "id":i
#             }
#         db.add_to_table(response_message)

#     for i in range(20):
#         response_message = {
#                 "from":alph[i],
#                 "text": "",
#                 "to": alph[i+1],
#                 "time": get_time(),
#                 "command": "-delivery_confirmed:",
#                 "delay": 0,
#                 "id":i
#             }
#         db.add_to_table(response_message)
#     table_array = db.get_all_tbl()
#     for table in table_array:
#         db.print_tbl(table)
#         print("messages from table: ",table)
#     print(db.is_such_table("[a|c]"))
