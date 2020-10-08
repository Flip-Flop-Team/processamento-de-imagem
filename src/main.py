import sys
import os
from PyQt5.QtCore import QCoreApplication, Qt, QT_TR_NOOP as tr
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QFileDialog, QAction
from widgets.imageWidget import ImageWidget


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.handleWindowDimensions()
        self.setWindowTitle('Detector de cancêr de mama')
        self.setIcon()
        self.topMenu()
        self.show()

    def handleWindowDimensions(self):
        screen = QtWidgets.QDesktopWidget().screenGeometry(-1)
        self.screenWidth = screen.width()
        self.screenHeight = screen.height()
        self.windowWidth = 800
        self.windowHeight = 500
        self.windowXInitialPosition = round(
            self.screenWidth/2-self.windowWidth/2)
        self.windowYInitialPosition = round(
            self.screenHeight/2-self.windowHeight/2)
        self.setGeometry(self.windowXInitialPosition,
                         self.windowYInitialPosition, self.windowWidth, self.windowHeight)

    def setIcon(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.setWindowIcon(QIcon(os.path.join(path, 'assets/icon.png')))

    def topMenu(self):
        topMenu = self.menuBar()
        fileMenu = topMenu.addMenu('&File')
        fileMenu.addAction(self.createTopMenuAction(
            '&Open Image', 'Ctrl+O', 'Open a image', self.openImage))

    def createTopMenuAction(self, text, shortcut, statusTip, func):
        action = QAction(text, self)
        action.setShortcut(shortcut)
        action.setStatusTip(statusTip)
        action.triggered.connect(func)
        return action

    def openImage(self):
        imagePath, _ = QFileDialog.getOpenFileName(
            self, 'Open Image', '', '*.png *.TIFF *.DICOM')
        imageBackground = ImageWidget(imagePath, self)
        self.currentWidget = imageBackground
        self.setCentralWidget(self.currentWidget)


if __name__ == "__main__":  # had to add this otherwise app crashed
    def run():
        app = QApplication(sys.argv)
        Gui = MainWindow()
        sys.exit(app.exec_())
run()
