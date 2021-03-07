from PyQt5.QtWidgets import QApplication, QFrame
from PyQt5.QtWidgets import QDialog, QLabel, QGridLayout
from PyQt5 import uic
from PyQt5.QtCore import QTimer
import sys
from threading import Timer
# TODO: design decent message styling
# Todo: display time info for message
# TODO: send messages with enter button


class Gui():
    def __init__(self, window, client, message_arr):  # ? class, instance<- -> None
        self.window_class = window
        self.window = None
        self.client = client
        self.messages_to_display = message_arr
        self.timer = QTimer()
        self.to_check_status = True

    def start(self):
        self.setup_qtimer()
        app = QApplication([])  # in properties there will be account_name
        self.window = self.window_class(self.client)
        self.window.show()
        self.timer.start()
        sys.exit(app.exec_())

    def check_status(self):
        is_existent = self.client.chat_account_is_existent
        is_online = self.client.chat_account_is_online
        is_checked = self.client.chat_account_status_checked
        if is_checked == None:
            pass
        elif is_checked == False:
            print(is_existent,is_online)

            if is_existent == True:
                if is_online == True:
                    self.window.change_button_color(self.window.select_button, self.window.online_button_color)
                else:
                    self.window.change_button_color(
                        self.window.select_button, self.window.offline_button_color)
                    
                self.client.chat_account_status_checked = True    
            else:
                self.window.change_button_color(
                    self.window.select_button, self.window.error_button_color)
                self.window.clear_field(self.window.account_field)
                self.client.chat_account_status_checked = None

        elif is_checked == True:
            if self.to_check_status:
                self.client.chat_account_status_checked = None
                self.client.get_account_status(self.window.select_button_value)
            else:
                pass
        return

    def display_message_arr(self):
        for i in range(len(self.messages_to_display)):
            new_message_matrix = self.messages_to_display[i]
            text = new_message_matrix[0]
            status_vals = new_message_matrix[1]
            #!rewrite
            if len(status_vals) == 1:  # ! in case it wasn't message sent from this account
                self.window.create_message_tab(
                    text, from_this_account=False)
            else:
                is_read = status_vals[1]
                self.window.create_message_tab(
                    text, from_this_account=True, is_read=is_read)
                
                if is_read:
                    highlight_timer = Timer(0.5,self.highlight_message,(self.window.last_msg_ind,))
                    highlight_timer.start()

    def setup_qtimer(self):  # ? None < -- --> None
        self.timer.setInterval(1000)  # check message and status
        self.timer.timeout.connect(self.check_messages)

    def check_messages(self):  # ? None < -- --> None
        if self.messages_to_display != []:
            self.display_message_arr()
            self.messages_to_display.clear()
        self.check_status()

    def highlight_message(self, id):  # ? (int)->None
        self.window.highlight_message_tab(id)  # change status to read
        return None
#! array of widget isn't added


class Main_Window(QDialog):

    def __init__(self, client):
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

        #! font styles don't work, need to use Qfont object!
        self.message_height = 50  # height in px
        self.message_font_size = 20
        self.message_font_color = "white"

        # *select button styles
        self.processing_button_color = "yellow"
        self.error_button_color = "red"
        self.offline_button_color = "#00ff7f"
        self.online_button_color = "#009900"

        self.another_account_message_color = "#FFFFFF"  # white color
        self.this_account_unread_message_color = "#DCDCDC"  # gray
        self.this_account_read_message_color = "#DCFBB7"  # light_green
        self.select_button_value = ""
        self.new_msg_ind = 0
        self.last_msg_ind = self.new_msg_ind-1

    def setup_widgets(self):  # ? ..<- -> None
        self.send_button.clicked.connect(self.send_button_clicked)
        self.select_button.clicked.connect(self.select_button_clicked)
        self.scrollArea.setWidgetResizable(True)
        self.widget.setLayout(self.layout)
        self.scrollArea.setWidget(self.widget)
        self.scrollArea.focusNextPrevChild(True)
        return None

    def closeEvent(self, *args, **kwargs):  # ? None <-- --> None
        print("Quitting client")
        self.client.exit_client()
        return None

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

    def change_button_color(self, button, color):  # ? obj inst, string<-- --> None
        button.setStyleSheet(f"background-color:{color}")
        return None

    def send_button_clicked(self):  # ? ..<- -> None

        recipient_account = self.get_account_val()
        if recipient_account:
            text = self.get_message_text()
            if text:
                self.clear_field(self.message_field)
                delay = self.get_delay()[0]  # gets only hour
                message = self.compose_message(recipient_account, text, delay)
                if recipient_account == self.client.account:
                    is_read = True
                else:
                    is_read = False
                self.create_message_tab(
                    text, from_this_account=True, is_read=is_read)
                self.client.send_message_obj(message)
            else:
                pass
            return None

    def clear_field(self, field):  # ? object inst<-- --> None
        field.clear()
        return None

    def get_account_val(self):  # ? ()->
        recipient_account = self.client.chat_account
        return recipient_account

    # ? string, int (arr in future ) <-- --> dict
    def compose_message(self, account, text, delay):
        msg = {
            "to": account,
            "from": self.client.account,
            "delay": delay,
            "text": text,
            "command": "-s:",
            "time": self.client.get_time(),
            "id": self.new_msg_ind
        }
        return msg

    
    
    def select_button_clicked(self):  # ? ..<- -> None
        #! firstly we need to check in a local database, when in global(server database)
        recipient_account_value = self.account_select.text()
        self.select_button_value = recipient_account_value
        self.remove_message_tabs()
        self.client.get_account_status(recipient_account_value)
        self.change_button_color(self.select_button, "yellow")
        self.reset_message_index()
        self.client.display_chat()
        print("prompting server for chat history!  line 193 gui.py")
        return None

    def reset_message_index(self):
        self.new_msg_ind = 0
        self.last_msg_ind = self.new_msg_ind-1
    
    def auto_scroll(self):
        scroll_timer = Timer(1.0, self.scroll_to_message)
        scroll_timer.start()
        return None

    def scroll_to_message(self):
        self.scrollbar.setValue(self.scrollbar.maximum())
        return None

    # ? string ,bool<- -> none
    def create_message_tab(self, text, from_this_account=False, is_read=False):
        self.new_msg_ind += 1
        self.last_msg_ind+=1
        new_tab = QLabel(self.scrollArea)
        backgnd_color = self.define_background_color(
            from_this_account, is_read)
        new_tab.setText(text)
        new_tab.setStyleSheet(
            f"background-color:{backgnd_color};font:{self.message_font_size}px {self.message_font_color} Arial")
        new_tab.setFixedHeight(self.message_height)
        self.layout.addWidget(new_tab)
        new_tab.show()
        self.auto_scroll()
        return None

    # ?(bool,bool,bool)->string
    def define_background_color(self, from_this_account, is_read):
        if from_this_account == False:

            backgnd_color = self.another_account_message_color
        else:
            if is_read == True:
                backgnd_color = self.this_account_read_message_color
            else:
                backgnd_color = self.this_account_unread_message_color  # light gray
        return backgnd_color

    def remove_message_tabs(self):  # ? () -> None
        layout = self.layout
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)
        return None

    def highlight_message_tab(self, ind):
        
        message_widget = self.layout.itemAtPosition(ind, 0).widget()
        new_color = self.this_account_read_message_color  # !read_message_color
        message_widget.setStyleSheet(f"background-color:{new_color}")
        return None
