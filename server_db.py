import sqlite3
from random import randint
from queue import Queue
from threading import Event, Thread
# TODO : INTEGRATE SERVER WITH A DATABASE

alph = "abcdef"


class DB_Manager:
    def __init__(self):
        self.connection = sqlite3.connect("serv.db", check_same_thread=False)
        self.db_path = "serv.db"
        self.to_drop = True
        self.sql_queue = Queue(100)

    def setup(self):  # ?None<--  -->None
        cursor = self.connection.cursor()
        try:
            if self.to_drop:
                cursor.execute('''DROP TABLE MAIN_TABLE''')
                cursor.execute('DROP TABLE UNREAD_MESSAGES')
        except:
            pass
        cursor.execute('''CREATE TABLE MAIN_TABLE
                            (
                                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                account_name TEXT,
                                is_online INTEGER
                            )''')
        cursor.execute('''CREATE TABLE UNREAD_MESSAGES
                            (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                message_text TEXT,
                                recipient_account TEXT,
                                date TEXT
                            )''')
        self.connection.commit()
        self.test_fill()
        self.get_tbl("MAIN_TABLE")
        return

    def update_unsent_messages(self, message_text, recipient_account, date):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO UNREAD_MESSAGES(message_text,recipient_account,date) VALUES(?,?,?)",
                       (message_text, recipient_account, date))
        self.connection.commit()
        return

    def get_unsent_messages(self,account_name):
        cursor = self.connection.cursor()
        arr = cursor.execute("SELECT * FROM UNREAD_MESSAGES WHERE recipient_account==?",account_name).fetchall()
        arr = list(map(lambda elem:elem[1],arr))   
        self.connection.commit()     
        return arr
    # deletes all messages that were for some account
    def delete_unsent_messages(self, account_name):
        cursor = self.connection.cursor()

        cursor.execute(
            "DELETE FROM UNREAD_MESSAGES WHERE recipient_account==?", (account_name))
        self.connection.commit()
        # self.get_tbl("UNREAD_MESSAGES")
        return 

    def test_fill(self):  # ? None <-- -->None
        cursor = self.connection.cursor()

        for letter in alph:
            cursor.execute(
                '''INSERT INTO {}(account_name,is_online) VALUES (?,?)'''.format("MAIN_TABLE"), (letter, 0))
        self.connection.commit()
        return

    def get_tbl(self, table):  # ? None<-- --> None
        cursor = self.connection.cursor()
        for row in cursor.execute('''SELECT * FROM {}'''.format(table)):
            print(row)
        return
        
    def update_value(self, table, account_name, column, value):  # ? None<-- -->None
        cursor = self.connection.cursor()
        cursor.execute(
            'UPDATE {} SET {}={} WHERE account_name==?'.format(table, column, value), account_name)
        self.connection.commit()
        self.get_tbl("MAIN_TABLE")
        return
    #!sqlite3.ProgrammingError:
    #!Incorrect number of bindings supplied. The current statement uses 1, and there are 2 supplied.
    def is_existent(self, account_name):  # ? string<-- --> bool
        cursor = self.connection.cursor()
        value = cursor.execute(
            'SELECT is_online from MAIN_TABLE WHERE account_name==?', (account_name,))
        self.connection.commit()
        if value.fetchall() == []:
            return False
        else:
            return True 

    def is_online(self, account_name):  # ? string<--  -->bool
        cursor = self.connection.cursor()
        for row in cursor.execute('SELECT is_online from MAIN_TABLE WHERE account_name==?', account_name):
            is_online = row[0]
            if is_online:
                return True
            else:
                return False
        self.connection.commit()
        del cursor


# def a():
#     print("here")
#     print(manager.is_online("a"))


manager = DB_Manager()
manager.setup()

accounts = "abcdef"
string = "slakdajsfdkjasdfljlasdfjlawjelkjds"
for i in range(100):
    manager.update_unsent_messages(string[0:randint(
        1, len(string)-2)], accounts[randint(0, len(accounts)-1)], "hello")
print(manager.get_unsent_messages("a"))
print(manager.is_existent("asdfasdfas"),"is existent")

print(manager.delete_unsent_messages("d"))
print(manager.get_unsent_messages("d"))


#! MESSAGE DELETION WORKS PROPERLY
