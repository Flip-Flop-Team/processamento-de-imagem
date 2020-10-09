from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel


class ImageWidget(QtWidgets.QWidget):
    def __init__(self, imagePath, MainWindow):
        super(ImageWidget, self).__init__()
        print(imagePath)
        self.originalPixmap = QPixmap(imagePath)
        self.pixmap = self.originalPixmap
        self.label = QLabel(self)
        self.label.setPixmap(self.pixmap)
        self.scale = 1

    def wheelEvent(self, event):
        side = int(event.angleDelta().y()/120)
        if (self.scale < 5 and side > 0) or (self.scale > 0.5 and side < 0):
            self.scale += side/10
        self.pixmap = self.originalPixmap.scaled(
            self.originalPixmap.width()*self.scale, self.originalPixmap.height()*self.scale)
        self.label.setPixmap(self.pixmap)
        self.label.adjustSize()
