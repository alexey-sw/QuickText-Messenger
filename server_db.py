import sqlite3
# TODO : INTEGRATE SERVER WITH A DATABASE

alph = "abcdef"


class Manager:
    def __init__(self):
        self.connection = sqlite3.connect("serv.db")
        self.db_path = "serv.db"
        self.cursor = self.connection.cursor()

    def setup(self):
        try:
            self.cursor.execute('''DROP TABLE MAIN_TABLE''')
        except:
            pass
        self.cursor.execute('''CREATE TABLE MAIN_TABLE
                            (
                                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                account_name TEXT,
                                is_online INTEGER
                            )''')

        self.connection.commit()
        self.test_fill()
        self.get_main_tbl()

    def test_fill(self):
        for letter in alph:
            self.cursor.execute(
                '''INSERT INTO {}(account_name,is_online) VALUES (?,?)'''.format("MAIN_TABLE"), (letter, 0))
        self.connection.commit()
        return

    def get_main_tbl(self):
        for row in self.cursor.execute('''SELECT * FROM MAIN_TABLE'''):
            print(row)
        return

    def update_value(self, table,account_name,column,value):
        self.cursor.execute(
            'UPDATE {} SET {}={} WHERE account_name==?'.format(table,column,value),account_name)
        self.connection.commit()
        self.get_main_tbl()

    def is_existent(self, account_name):
        for row in self.cursor.execute('SELECT is_online from MAIN_TABLE WHERE account_name==?',account_name):
            return True
        return False
        
    def is_online(self,account_name):
        for row in self.cursor.execute('SELECT is_online from MAIN_TABLE WHERE account_name==?',account_name):
            is_online = row[0]
            if is_online:
                return True
            else:
                return False
        
        
Manager = Manager()
Manager.setup()
Manager.update_value("MAIN_TABLE","a", "is_online", 1)
print(Manager.is_online("a"))
print(Manager.is_online("b"))
Manager.is_existent("a")
print(Manager.is_existent("m"))