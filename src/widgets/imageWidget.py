from PyQt5.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor, QPen
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QScrollArea
from PyQt5 import QtCore
from PyQt5 import Qt
import cv2
import copy


class ImageWidget(QtWidgets.QWidget):
    def __init__(self, imagePath, MainWindow):
        super(ImageWidget, self).__init__()
        mainWindowSize = copy.deepcopy(MainWindow.size())
        mainWindowSize.setHeight(mainWindowSize.height()-30)
        self.resize(mainWindowSize)
        self.originalPixmap = QPixmap(imagePath)
        self.zoomedPixmap = self.originalPixmap
        self.scrollArea = QScrollArea(self)
        self.scrollArea.resize(self.size())
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.label = QLabel()
        self.label.setPixmap(self.originalPixmap)
        self.label.resize(self.originalPixmap.size())
        self.scrollArea.setWidget(self.label)
        self.scale = 1

        #Modes
        self.drawReact = False
        self.zoom = False
        
        self.mousePosition = QtCore.QPoint()
        self.label.setMouseTracking(True)
        self.scrollArea.setMouseTracking(True)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        self.mousePosition = event.pos()
        self.update()

    def mousePressEvent(self, e):
        self.drawReact = False

    def zoomFunction(self, direction):
        if (self.scale < 5 and direction > 0) or (self.scale > 0.5 and direction < 0):
            self.scale += direction/10
        self.zoomedPixmap = self.originalPixmap.scaled(
            self.originalPixmap.width()*self.scale, self.originalPixmap.height()*self.scale)
        self.label.setPixmap(self.zoomedPixmap)
        self.label.resize(self.zoomedPixmap.size())

    def paintEvent(self, e):
        if self.drawReact:
            x = self.mousePosition.x()+self.scrollArea.horizontalScrollBar().value()
            y = self.mousePosition.y()+self.scrollArea.verticalScrollBar().value()
            pixmapX = self.zoomedPixmap.size().width()
            pixmapY = self.zoomedPixmap.size().height()

            if x < 64: x = 64
            if y < 64: y = 64
            if x > pixmapX-64: x = pixmapX-64
            if y > pixmapY-64: y = pixmapY-64

            self.label.setPixmap(self.zoomedPixmap)
            qp = QPainter(self.label.pixmap())
            qp.setPen(QPen(QColor(0, 255, 0), 3, QtCore.Qt.SolidLine))
            br = QBrush(QColor(0, 0, 0, 0))
            qp.setBrush(br)
            firstPoint = copy.deepcopy(self.mousePosition)
            secondPoint = copy.deepcopy(self.mousePosition)
            firstPoint.setX(x-64)
            firstPoint.setY(y-64)
            secondPoint.setX(x+64)
            secondPoint.setY(y+64)
            self.p1x = firstPoint.x()
            self.p1y = firstPoint.y()
            self.p2x = secondPoint.x()
            self.p2y = secondPoint.y()
            qp.drawRect(QtCore.QRect(firstPoint, secondPoint))