from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel


class BlackWindow(QtWidgets.QWidget):
    def __init__(self):
        super(BlackWindow, self).__init__()
        self.setStyleSheet("background-color: black;")
        self.setWindowTitle("Color")
        self = QLabel(self)
        self.resize(800, 500)
