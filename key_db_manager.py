import sqlite3
from encryption import *
#! import statement
# key manager must be able to work with existing db
# Todo: store key as bytes


class Key_Manager:
    def __init__(self):
        self.db_dir = "key_db.db"
        self.connection = sqlite3.connect(self.db_dir, check_same_thread=False)
        self.to_drop = False

    def setup(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute("""CREATE TABLE ENCRYPTION_KEYS
                           (
                                KEY_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                CHAT TEXT,
                                KEY BLOB
                            )""")
        except:
            print("Table with encryption keys has already been created")
        self.connection.commit()
        del cursor
        return None

    def set_key(self, chat):  # ? (string)->None
        """ Sets unique key for every chat """
        cursor = self.connection.cursor()
        key = generate_key()
        print(len(key), " -length of the key")
        print(key, "generated key ")
        cursor.execute(
            'INSERT INTO ENCRYPTION_KEYS(CHAT,KEY) VALUES (?,?)', (chat, key))
        self.connection.commit()
        del cursor
        return None

    def drop_tbl(self, table):  # ?(string)->None
        cursor = self.connection.cursor()
        cursor.execute("DROP TABLE {};".format(table))
        self.connection.commit()
        return None
    
    def delete_keys(self):
        cursor = self.connection.cursor()
        self.drop_tbl("ENCRYPTION_KEYS")
        self.setup()
        self.connection.commit()
        del cursor
        return None

    def key_exists(self, table_name):  # ? (string)-> bool
        cursor = self.connection.cursor()
        print(table_name)
        key = cursor.execute(
            "SELECT KEY FROM ENCRYPTION_KEYS WHERE CHAT = (?)", (table_name,)).fetchall()
        self.connection.commit()
        del cursor
        if key:
            return True
        else:
            return False

    def format_key_output(self, output):  # ? (matrix)->string
        key = output[0][0]
        print("Formatted key ", key)
        return key

    def retrieve_key(self, table):  # ? (string)-> string
        cursor = self.connection.cursor()
        key = cursor.execute(
            "SELECT KEY FROM ENCRYPTION_KEYS WHERE CHAT = (?)", (table,)).fetchall()
        key = self.format_key_output(key)
        self.connection.commit()
        del cursor
        return key

    def decode_message_matrix(self, matrix, table):
        decode_key = self.retrieve_key(table)
        print(len(decode_key))
        matrix = list(map(lambda message: decrypt(
            message[1], decode_key), matrix))
        print("Decoded matrix : ", matrix)
        return matrix

# km = Key_Manager()
# km.setup()
# km.set_key("[a|b]")
# km.retrieve_key("[a|b]")
