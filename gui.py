import PyQt5
from PyQt5.QtWidgets import QApplication, QTextBrowser, QWidget, QFrame
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QLabel, QGridLayout
from PyQt5 import uic
from PyQt5 import QtGui

class Gui():
    def __init__(self, window,client):  # ? class, instance<- -> None
        self.window_class = window
        self.window = None
        self.client = client 

    def start(self):
        app = QApplication([])  # in properties there will be account_name
        self.window = self.window_class(self.client)
        self.window.show()
        app.exec_()


class Main_Window(QDialog):

    def __init__(self,client):
        super().__init__()
        self.client = client
        uic.loadUi("messenger_gui.ui", self)
        self.send_button = self.send_button
        self.select_button = self.select_button
        self.timer = self.timeEdit
        # need to add widget into a scroll area with layout
        self.scrollArea = self.messageArea
        self.widget = QFrame()
        self.layout = QGridLayout()
        self.setup_widgets()
        self.message_field = self.message_edit  # message text input
        self.h = 200

    def closeEvent(self, *args, **kwargs):
        
        print("hello world ")
        self.client.exit_client()

    def get_delay(self):  # ? ...<- -> array of int
        delay_obj = self.timer.dateTime()
        delay_str = delay_obj.toString()
        colon_ind = delay_str.index(":")
        hours = int(delay_str[colon_ind-2:colon_ind])
        mins = int(delay_str[colon_ind+1:colon_ind+3])
        return [hours, mins]

    def get_message_text(self):  # ? ..<- -> string
        text = self.message_field.text()
        self.message_field.clear()
        return text

    def send_button_clicked(self):  # ? ..<- -> None
        text = self.get_message_text()
        delay = self.get_delay()[0]  # gets only hours
        self.create_message_tab(text)
        return

    def setup_widgets(self):  # ? ..<- -> None
        self.send_button.clicked.connect(self.send_button_clicked)
        self.select_button.clicked.connect(self.select_button_clicked)
        self.scrollArea.setWidgetResizable(True)
        self.widget.setLayout(self.layout)
        self.scrollArea.setWidget(self.widget)
        self.scrollArea.focusNextPrevChild(True)
        return None

    def select_button_clicked(self):  # ? ..<- -> None
        print("select_button_clicked")
        return None

    def create_message_tab(self, text, from_this_device=False):  # ? string ,bool<- -> none
        new_tab = QLabel(self.scrollArea)
        backgnd_color = "#a3ffdc" if not(from_this_device) else "#a2f481"
        new_tab.setText(text)
        new_tab.setStyleSheet(
            f"background-color:{backgnd_color};font:20px Arial")
        new_tab.setFixedHeight(50)
        self.layout.addWidget(new_tab)
        new_tab.show()
        self.h += 200

        return



