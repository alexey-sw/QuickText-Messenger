from PyQt5 import Qt
from PyQt5.QtWidgets import QGridLayout, QLabel,QHBoxLayout


app = Qt.QApplication([])

layout = QGridLayout()

for i in range(10):
    for j in range(5):
        label = QLabel()
        label.setText("hello")
        layout.addWidget(label, i, j)

w = Qt.QWidget()
w.setLayout(layout)

mw = Qt.QScrollArea()
mw.setWidget(w)
mw.resize(200, 200)
mw.show()
for i in range(10):
    for j in range(5):
        label = QLabel()
        label.setText("hello")
        layout.addWidget(label, i, j)


app.exec()