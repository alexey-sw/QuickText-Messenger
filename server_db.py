import sqlite3
from random import randint
from queue import Queue
from threading import Event
# TODO : INTEGRATE SERVER WITH A DATABASE

alph = "abcdef"


class DB_Manager:
    def __init__(self):
        self.connection = sqlite3.connect("serv.db")
        self.db_path = "serv.db"
        self.cursor = self.connection.cursor()
        self.to_drop = True 
        self.sql_queue = Queue(100) 
        self.flag = Event()        
        
    def setup(self):  # ?None<--  -->None
        try:
            if self.to_drop:
                self.cursor.execute('''DROP TABLE MAIN_TABLE''')
                self.cursor.execute('DROP TABLE UNREAD_MESSAGES')
        except:
            pass
        self.cursor.execute('''CREATE TABLE MAIN_TABLE
                            (
                                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                account_name TEXT,
                                is_online INTEGER
                            )''')
        self.cursor.execute('''CREATE TABLE UNREAD_MESSAGES
                            (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                message_text TEXT,
                                recipient_account TEXT,
                                date TEXT
                            )''')
        self.connection.commit()
        self.test_fill()
        self.get_tbl("MAIN_TABLE")
        self.refresh()
        return

    def update_unsent_messages(self, message_text, recipient_account, date):
        self.cursor.execute("INSERT INTO UNREAD_MESSAGES(message_text,recipient_account,date) VALUES(?,?,?)",(message_text,recipient_account,date))
        self.connection.commit()
        return 
    def check_queue(self):
        pass
    
    def refresh(self):
        self.flag.wait()
        self.execute_sql_queue()
        self.flag.clear()
        self.refresh()
    
    def execute_sql_queue(self):
        while not self.sql_queue.empty():
                instr_set = self.sql_queue.get()
                instruction = instr_set[0]
                argument = instr_set[1]
                instruction(argument)
        return       
                
    def delete_unsent_messages(self,account_name): # deletes all messages that were for some account 
        self.cursor.execute("DELETE FROM UNREAD_MESSAGES WHERE recipient_account==?",(account_name))
        self.connection.commit()
        self.get_tbl("UNREAD_MESSAGES")
    
    def test_fill(self):  # ? None <-- -->None
        for letter in alph:
            self.cursor.execute(
                '''INSERT INTO {}(account_name,is_online) VALUES (?,?)'''.format("MAIN_TABLE"), (letter, 0))
        self.connection.commit()
        return

    def get_tbl(self, table):  # ? None<-- --> None
        for row in self.cursor.execute('''SELECT * FROM {}'''.format(table)):
            print(row)
        return

    def update_value(self, table, account_name, column, value):  # ? None<-- -->None
        self.cursor.execute(
            'UPDATE {} SET {}={} WHERE account_name==?'.format(table, column, value), account_name)
        self.connection.commit()
        self.get_tbl("MAIN_TABLE")
        return

    def is_existent(self, account_name):  # ? string<-- --> bool
        value = self.cursor.execute(
            'SELECT is_online from MAIN_TABLE WHERE account_name==?', account_name)
        if value.arraysize:
            return True
        else:
            return False

    def is_online(self, account_name):  # ? string<--  -->bool
        print("checking if online")
        for row in self.cursor.execute('SELECT is_online from MAIN_TABLE WHERE account_name==?', account_name):
            is_online = row[0]
            print(is_online)
            if is_online:
                return True
            else:
                return False

# manager = DB_Manager()
# manager.setup()
# print(manager.is_online("a"))
# accounts = "abcdef"
# string = "slakdajsfdkjasdfljlasdfjlawjelkjds"
# for i in range(100):
#     manager.update_unsent_messages(string[0:randint(1,len(string)-2)],accounts[randint(0,len(accounts)-1)],"hello")
# manager.delete_unsent_messages("d")
# manager.get_tbl("UNREAD_MESSAGES")


#! MESSAGE DELETION WORKS PROPERLY 
  