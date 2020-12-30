import PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow,QTextBrowser,QWidget
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QLabel,QGridLayout
from PyQt5 import uic
from PyQt5 import Qt

class Gui():
    def __init__(self, window):
        self.window_class = window
        self.window = None

    def start(self):
        app = QApplication([])  # in properties there will be account_name
        self.window = self.window_class()
        self.window.show()
        app.exec_()


class Main_Window(QDialog):

    def __init__(self):
        super().__init__()
        uic.loadUi("messenger_gui.ui", self)
        self.send_button = self.send_button
        self.select_button = self.select_button
        self.timer = self.timeEdit
        self.scrollArea = Qt.QScrollArea(self) # need to add widget into a scroll area with layout 
        self.widget =QWidget()

        self.connect_widgets()
        self.message_field = self.message_edit  # message text input
        self.h = 200

        
        
    def get_delay(self):
        delay_obj = self.timer.dateTime()
        delay_str = delay_obj.toString()
        colon_ind = delay_str.index(":")
        hours = int(delay_str[colon_ind-2:colon_ind])
        mins = int(delay_str[colon_ind+1:colon_ind+3])
        return [hours, mins]

    def get_message_text(self):
        text = self.message_field.text()
        self.message_field.clear()
        
        return text

    def send_button_clicked(self):
        text = self.get_message_text()
        delay = self.get_delay()[0]  # gets only hours
        self.create_message_tab("hello")
        print(text)
        print(delay)

    def connect_widgets(self):
        global layout
       
        self.send_button.clicked.connect(self.send_button_clicked)
        self.select_button.clicked.connect(self.select_button_clicked)
        layout = QGridLayout()
        self.scrollArea.setLayout(layout)
        for i in range(5):
            label = QLabel("helo")
            layout.addWidget(label)
        self.scrollArea.setGeometry(200,200,200,200)
        self.scrollArea.show()

    def select_button_clicked(self):
        print("select_button_clicked")

    def create_message_tab(self, text, from_this_device=False):
        new_tab = QLabel(self.scrollArea)
        
        new_tab.setText("helwlleoajefajiiefjinsdf")
        new_tab.setStyleSheet("background-color:green;")
        new_tab.setGeometry(200, self.h, 200, 200)
        new_tab.setMargin(20)
        layout.addWidget(new_tab)
        print("added")
        new_tab.show()
        self.h+=200


GUI = Gui(Main_Window)
GUI.start()


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = Main_Window()
#     ex.show()
#     sys.exit(app.exec_())
