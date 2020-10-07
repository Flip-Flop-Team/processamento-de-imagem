from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel


class ImageWidget(QtWidgets.QWidget):
    def __init__(self, imagePath, MainWindow):
        super(ImageWidget, self).__init__()
        print(imagePath)
        pixmap = QPixmap(imagePath)
        self.label = QLabel(self)
        self.label.setPixmap(pixmap)
        MainWindow.resize(pixmap.size())
