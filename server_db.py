import sqlite3
#TODO : INTEGRATE SERVER WITH A DATABASE


alph = "abcdef"
class Manager:
    def __init__(self):
        self.connection = sqlite3.connect("serv.db")
        self.db_path = "serv.db"
        self.cursor = self.connection.cursor()
        self.id = 1
    
    def setup(self):
        self.cursor.execute('''DROP TABLE MAIN_TABLE''')
        self.cursor.execute('''CREATE TABLE MAIN_TABLE(user_id INT PRIMARY KEY,login TEXT,is_online INT)''')
        self.connection.commit()
        self.test_fill()
    def test_fill(self):
        for letter in alph:
            self.cursor.execute('''INSERT INTO MAIN_TABLE VALUES (?,?,?)''',(self.id,letter,0))
            self.id+=1
        self.connection.commit()

Manager = Manager()
Manager.setup()
