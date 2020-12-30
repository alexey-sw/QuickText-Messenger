from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel,QDialog
from PyQt5 import uic


class Gui():
    def __init__(self,window):
        self.window_class = window  
        self.window = None 
    def start(self):
        app = QApplication([])# in properties there will be account_name 
        self.window = self.window_class()
        self.window.show()
        app.exec_()
        self.window.get_delay()
        
class Main_Window(QDialog):
    
    def __init__(self):
        super().__init__()
        uic.loadUi("messenger_gui.ui", self)
        self.send_button = self.pushButton
        self.timer = self.timeEdit
        self.scrollArea = self.scrollArea
        self.connectAll()
        
    def get_delay(self):
        delay = self.timer.dateTime()
        print(delay)
        
    def connectAll(self):
        self.send_button.clicked.connect(hello)#
def hello():
    print("Button clicked")
        
GUI = Gui(Main_Window)  
GUI.start()

        

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = Main_Window()
#     ex.show()
#     sys.exit(app.exec_())
    
    
    
    
    
    
    
    
 