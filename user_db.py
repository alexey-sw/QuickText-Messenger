import sqlite3
import time

DEFAULT_TABLE = "sqlite_sequence"
# Todo: rename file into chat_db.py


class User_db:
    def __init__(self):  # ? (string)->None
        self.db_dir = "user_db.db"
        self.connection = sqlite3.connect(self.db_dir, check_same_thread=False)
        self.to_drop = False

    def setup(self):  # ? ()-> None
        print(self.get_all_tbl())
        if self.to_drop:
            for table in self.get_all_tbl():
                if table != DEFAULT_TABLE:
                    self.drop_tbl(table)

        return None

    def get_all_tbl(self):  # ?()->[of string]
        cursor = self.connection.cursor()
        table_array = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        self.connection.commit()
        table_array = list(map(lambda elem: "["+elem[0]+"]", table_array))
        return table_array

    def ensure_table_existent(self,account1,account2):
        table_name = self.compose_table_name(account1, account2)
        if self.is_such_table(table_name):
            pass
        else:
            self.register_user_pair(account1,account2)
        return None 
            



    def log_message(self, message):  # ?(string,dict)->None
        account_from = message["from"]
        account_to = message["to"]
        self.ensure_table_existent(account_from,account_to)
        table_name = self.compose_table_name(account_from,account_to)
        cursor = self.connection.cursor()
        date = message["time"]
        text = message["text"]
        message_id = message["id"]
        is_read = 0
        if account_from == account_to:
            is_read = 1
        print("appended message to table: ", table_name)
        cursor.execute("""INSERT INTO {}
            (
                MESSAGE_ID,
                SENDER,
                MESSAGE_TEXT,
                DATE,
                IS_READ
                ) VALUES(?,?,?,?,?)""".format(table_name), (message_id, account_from, text, date, is_read))
        self.connection.commit()
        return None

    # ?(string)->[[id(INT),text(string),date(string),IS_READ(bool)]]
    def retrive_messages(self, table):
        cursor = self.connection.cursor()
        if self.is_such_table(table):
            message_matrix = cursor.execute(
                """SELECT * FROM {}""".format(table)).fetchall()
            self.connection.commit()
            self.change_message_arr_status(table)
            return message_matrix
        else:
            return None

    def delete_messages(self):  # ? ()->None
        for table in self.get_all_tbl():
            if table != DEFAULT_TABLE:
                self.drop_tbl(table)

        self.get_all_tbl()
        print("here")
        return None

    def compose_table_name(self, first_account, second_account):  # ? (string)->string
        account_array = [first_account, second_account]
        account_array.sort()
        table_string = f"[{account_array[0]}|{account_array[1]}]"
        print(table_string)
        return table_string

    def print_tbl(self, table):  # ? (string)->None
        cursor = self.connection.cursor()
        for row in cursor.execute('''SELECT * FROM {}'''.format(table)):
            print(row)
        return None

    def change_message_arr_status(self, table):  # ? (string)->None
        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE {} SET IS_READ=1 WHERE IS_READ = 0".format(table))
        self.connection.commit()
        print("Message_arr_status changed: ")
        self.print_tbl(table)

        return None

    def create_table(self, table_name):  # ?(string) ->Bool
        cursor = self.connection.cursor()
        cursor.execute("""CREATE TABLE {}(
            MESSAGE_ID INTEGER PRIMARY KEY,
            SENDER TEXT,
            MESSAGE_TEXT TEXT,
            DATE TEXT,
            IS_READ INTEGER
            );
            """.format(table_name))
        self.connection.commit()
        return None

    def drop_tbl(self, table):  # ?(string)->None
        table = self.correct_table_spelling(table)
        cursor = self.connection.cursor()
        cursor.execute("DROP TABLE {};".format(table))
        self.connection.commit()
        return None

    def correct_table_spelling(self, table_name):  # ?(string)->string
        if not "[" or not "]" in table_name:
            table_name = f"[{table_name}]"
        else:
            pass
        return table_name

    def change_status(self, table, id):
        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE {} SET IS_READ=1 WHERE MESSAGE_ID = {}".format(table, id))
        self.connection.commit()
        self.print_tbl(table)
        return

    def is_such_table(self, table):  # ? (string) -> Bool
        table = self.correct_table_spelling(table)
        if not "[" or not "]" in table:
            table = f"[{table}]"
        table_array = self.get_all_tbl()
        if table in table_array:
            return True
        else:
            return False

    def register_user_pair(self, account_1, account_2):
        table_name = self.compose_table_name(account_1, account_2)
        self.create_table(table_name)
        return None

def get_time():
    return time.ctime()
