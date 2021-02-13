import sqlite3
from random import randint
from queue import Queue
from threading import Event, Thread


alph = "abcdef"
MAIN_TB = "MAIN_TABLE"


class DB_Manager:
    def __init__(self):
        self.db_dir = "serv.db"
        self.connection = sqlite3.connect(self.db_dir, check_same_thread=False)
        self.to_drop = False

    def setup(self):  # ?None<--  -->None
        cursor = self.connection.cursor()
        try:
            if self.to_drop:
                print("dropping main table ")
                cursor.execute('''DROP TABLE MAIN_TABLE''')
                cursor.execute('''CREATE TABLE MAIN_TABLE
                            (
                                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                account_name TEXT,
                                is_online INTEGER
                            )''')
        except:
            pass
        self.connection.commit()
        # self.test_fill()
        self.get_tbl("MAIN_TABLE")
        del cursor
        return None

    def delete_users(self):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM MAIN_TABLE")
        self.connection.commit()
        return None

    def get_tbl(self, table):  # ? None<-- --> None
        cursor = self.connection.cursor()
        for row in cursor.execute('''SELECT * FROM {}'''.format(table)):
            print(row)
        del cursor
        return None

    def update_value(self, table, account_name, column, value):  # ? None<-- -->None
        cursor = self.connection.cursor()
        cursor.execute(
            'UPDATE {} SET {}={} WHERE account_name==?'.format(table, column, value), account_name)
        self.connection.commit()
        del cursor
        return None

    def is_existent(self, account_name):  # ? string<-- --> bool
        cursor = self.connection.cursor()
        value = cursor.execute(
            'SELECT is_online from MAIN_TABLE WHERE account_name==?', (account_name,))
        self.connection.commit()
        del cursor
        if value.fetchall() == []:
            return False
        else:
            return True

    def disconnect_all(self):
        cursor = self.connection.cursor()
        table = "MAIN_TABLE"
        column = "is_online"
        value = 0
        cursor.execute('UPDATE {} SET {}={} '.format(table, column, value))
        self.connection.commit()
        return None

    def disconnect_user(self, account_name):  # ?(string)->None
        self.update_value(MAIN_TB, account_name, "is_online", 0)
        return None

    def connect_user(self, account_name):
        self.update_value(MAIN_TB, account_name, "is_online", 1)
        return None

    def append_client(self, account_name):
        cursor = self.connection.cursor()
        is_online = 1  # * if user has signed up, then he is online
        cursor.execute('''INSERT INTO {}(account_name,is_online) VALUES (?,?)'''.format(
            "MAIN_TABLE"), (account_name, 1))
        print("appending client: ", account_name)
        return None

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
        return None
