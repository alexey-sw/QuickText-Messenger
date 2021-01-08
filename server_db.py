import sqlite3
#TODO : INTEGRATE SERVER WITH A DATABASE

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
                                login TEXT,
                                is_online INTEGER
                            )''')
        
        self.connection.commit()
        self.test_fill()
        self.get_main_tbl()
          
    def test_fill(self):
        for letter in alph:
            self.cursor.execute('''INSERT INTO MAIN_TABLE(login,is_online) VALUES (?,?)''',(letter,0))
        self.connection.commit()
        return 
    
    def get_main_tbl(self):
        for row in self.cursor.execute('''SELECT * FROM MAIN_TABLE'''):
            print(row)
        return
    
    def update_value(self,table,id,field,value):
        pass
    
    def is_existent(self,account_name):
        pass 
    
    
Manager = Manager()
Manager.setup()
