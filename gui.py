import PyQt5
from PyQt5.QtWidgets import QApplication,QFrame
from PyQt5.QtWidgets import QDialog, QLabel, QGridLayout
from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5 import QtCore
import sys
import threading
# todo: add select value 
# todo: colorize messages that have been sent 

class Gui():    
    def __init__(self, window,client,message_arr):  # ? class, instance<- -> None
        self.window_class = window
        self.window = None
        self.client = client 
        self.messages_to_display = message_arr 
        self.timer =QTimer()

    def start(self):
        self.setup_qtimer()
        app = QApplication([])  # in properties there will be account_name
        self.window = self.window_class(self.client)
        self.window.show()
        self.timer.start()
        sys.exit(app.exec_())
        
    def check_status(self):
        is_existent = self.client.recipient_account_status["is_existent"]
        is_online = self.client.recipient_account_status["is_online"]
        is_checked = self.client.recipient_account_status["status_checked"]
        if is_checked==None:
            pass
        elif is_checked ==False:
            
            self.client.recipient_account_status["status_checked"]= True
            if is_existent==True:
                self.window.change_button_color(self.window.select_button,"#00ff7f")
                print("exists")
                if is_online==True:
                    self.window.change_button_color(self.window.select_button,"#009900")
                    print("online")
            else:
                self.window.change_button_color(self.window.select_button,"red")
                self.window.clear_field(self.window.account_field)

        elif is_checked ==True:
            self.client.recipient_account_status["status_checked"] = False 
            self.client.get_account_status(self.window.select_button_value)
            
    def check_delivered_messages(self):
        pass
    
    def setup_qtimer(self):#? None < -- --> None 
        self.timer.setInterval(1000)# check message and status 
        self.timer.timeout.connect(self.check_messages)
    
    def check_messages(self): #? None < -- --> None 
        if self.messages_to_display!=[]:
            for i in range(len(self.messages_to_display)):
                new_message = self.messages_to_display[i]
                self.window.create_message_tab(new_message,from_this_device = False)
            self.messages_to_display.clear()
        self.check_status()
        self.check_delivered_messages()
            
            
      


class Main_Window(QDialog):

    def __init__(self,client):
        super().__init__()
        self.client = client
        uic.loadUi("messenger_gui.ui", self)
        
        self.timer = self.timeEdit
        self.scrollArea = self.messageArea
        self.scrollbar = self.scrollArea.verticalScrollBar()
        
        self.widget = QFrame()
        self.layout = QGridLayout()
        self.setup_widgets()
        
        self.send_button = self.send_button
        self.select_button = self.select_button
        self.message_field = self.message_edit  # message text input
        self.account_field = self.account_select
        
        self.message_height = 30# height in px
        self.message_font_size = 14 
        
        self.select_button_value = ""
        self.widget_ind=0

    def closeEvent(self, *args, **kwargs): # ? None <-- --> None 
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
        text = str(self.message_field.text())
        return text
    
    def change_button_color(self,button,color): # ? obj inst, string<-- --> None 
        button.setStyleSheet(f"background-color:{color}")
        return None 
    
    def send_button_clicked(self):  # ? ..<- -> None
        
        recipient_account = self.get_account_val()
        if recipient_account:
            
        # does exist? 
            text = self.get_message_text()
            self.clear_field(self.message_field)
            delay = self.get_delay()[0]  # gets only hours
            self.create_message_tab(text,from_this_device=True)
            message = self.compose_message(recipient_account,text,delay)
            self.client.send_message_obj(message)
            return None 
    
    def clear_field(self,field):#? object inst<-- --> None 
        field.clear()
        return 
    
    def get_account_val(self):
        value = self.client.recipient_account_status["account"]
        return value 
    
    def compose_message(self,account,text,delay):  #? string, int (arr in future ) <-- --> dict 
        msg = {
            "to":account,
            "from":self.client.account,
            "delay":delay,
            "text":text,
            "command":"-s:",
            "time":self.client.get_time()
        }
        return msg 
    
    def setup_widgets(self):  # ? ..<- -> None
        self.send_button.clicked.connect(self.send_button_clicked)
        self.select_button.clicked.connect(self.select_button_clicked)
        self.scrollArea.setWidgetResizable(True)
        self.widget.setLayout(self.layout)
        self.scrollArea.setWidget(self.widget)
        self.scrollArea.focusNextPrevChild(True)
        return None

    def select_button_clicked(self,change_color = True):  # ? ..<- -> None 
        #! firstly we need to check in a local database, when in global(server database)
        recipient_account_value = self.account_select.text()
        self.select_button_value = recipient_account_value
        self.client.get_account_status(recipient_account_value)
        self.change_button_color(self.select_button,"yellow")
        return None
    
    def auto_scroll(self):
        scroll_timer = threading.Timer(1.0,self.scroll_to_message)
        scroll_timer.start()
    
    def scroll_to_message(self):
        self.scrollbar.setValue(self.scrollbar.maximum())
    
    def create_message_tab(self, text, from_this_device=False):  # ? string ,bool<- -> none
        new_tab = QLabel(self.scrollArea)
        backgnd_color = "#a3ffdc" if not(from_this_device) else "#a2f481"
        new_tab.setText(text)
        new_tab.setStyleSheet(
            f"background-color:{backgnd_color};font:{self.message_font_size}px Arial")
        new_tab.setFixedHeight(self.message_height)
        self.layout.addWidget(new_tab)
        # some_widget = self.layout.itemAt(self.widget_ind).widget()
        # self.widget_ind+=1
        # childarr = self.scrollArea.children()
        # for elem in childarr:
        #     print(str(elem.setStyleSheet("background-color:red")))
        new_tab.show()
        self.auto_scroll()
        return



