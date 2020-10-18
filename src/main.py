import sys
import os
from PyQt5.QtCore import QCoreApplication, Qt, QT_TR_NOOP as tr
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QFileDialog, QAction, QMessageBox
from widgets.imageWidget import ImageWidget
import signal
import pydicom as dicom
import cv2

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.handleWindowDimensions()
        self.setWindowTitle('Detector de cancêr de mama')
        self.setIcon()
        self.topMenu()
        self.show()
        self.characteristics = {}

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
        actionMenu = topMenu.addMenu('&Actions')
        trainingMenu = topMenu.addMenu('&Training')

        fileMenu.addAction(self.createTopMenuAction(
            '&Open Image', 'Ctrl+O', 'Open a image', self.openImage))
        fileMenu.addAction(self.createTopMenuAction('Open &folder', 'Ctrl+F', 'Open folder', self.openFolder))

        actionMenu.addAction(self.createTopMenuAction('&Select region', 'Ctrl+S', 'Select a region', self.selectRegion))
        actionMenu.addAction(self.createTopMenuAction('Z&oom', 'Ctrl+=', 'Zoom a image', self.zoomImage))
        actionMenu.addAction(self.createTopMenuAction('U&nzoom', 'Ctrl+-', 'Unzoom a image', self.unzoomImage))
        actionMenu.addAction(self.createTopMenuAction('Unselect all actions', 'Esc', 'Unselect all actions', self.unselect))

        trainingMenu.addAction(self.createTopMenuAction('Train', 'Ctrl+T', 'Train using images', self.train))
        trainingMenu.addAction(self.createTopMenuAction('Calculate characteristics', '', 'Calculate characteristics from images', self.calculate))
        trainingMenu.addAction(self.createTopMenuAction('Homogeneidade', '', 'Use homogeneidade', self.useHomogeneidade, True))
        trainingMenu.addAction(self.createTopMenuAction('Entropy', '', 'Use entropy', self.useEntropy, True))
        trainingMenu.addAction(self.createTopMenuAction('Variance', '', 'Use variance', self.useVariance, True))

    def train(self):
        self.showSuccessMessage('Training...')

    def calculate(self):
        self.showSuccessMessage('Calculating...')

    def useHomogeneidade(self, checked):
        self.characteristics['homogeneidade'] = checked
    def useEntropy(self, checked):
        self.characteristics['entropy'] = checked
    def useVariance(self, checked):
        self.characteristics['variance'] = checked

    def unselect(self):
        self.currentWidget.drawReact = False
        self.currentWidget.label.setPixmap(self.currentWidget.zoomedPixmap)

    def zoomImage(self):
        if hasattr(self, 'currentWidget'):
            size = self.currentWidget.originalPixmap.size()
            self.currentWidget.zoomFunction(1)
        else:
            self.showErrorMessage('You need to open a image first')

    def unzoomImage(self):
        if hasattr(self, 'currentWidget'):
            size = self.currentWidget.originalPixmap.size()
            self.currentWidget.zoomFunction(-1)
        else:
            self.showErrorMessage('You need to open a image first')

    def selectRegion(self):
        if hasattr(self, 'currentWidget'):
            size = self.currentWidget.originalPixmap.size()
            if size.width() < 128 or size.height() < 128:
                self.showErrorMessage('Image needs to be at least 128x128 pixels')
            else:
                self.currentWidget.drawReact = True
        else:
            self.showErrorMessage('You need to open a image first')
            

    def showErrorMessage(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(text)
        msg.setWindowTitle("Error")
        msg.exec_()

    def showSuccessMessage(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Success")
        msg.setInformativeText(text)
        msg.setWindowTitle("Success")
        msg.exec_()

    def createTopMenuAction(self, text, shortcut, statusTip, func, checkable=False):
        action = QAction(text, self, checkable=checkable)
        action.setShortcut(shortcut)
        action.setStatusTip(statusTip)
        action.triggered.connect(func)
        return action

    def openImage(self):
        imagePath, _ = QFileDialog.getOpenFileName(
            self, 'Open Image', '', '*.png *.TIFF *.DCM')
        if imagePath == "":
            return
        if '.DCM' in imagePath.lower():
            print('Opening a DICOM')
            ds = dicom.dcmread(imagePath)
            pixel_array_numpy = ds.pixel_array
            imagePath = imagePath.replace('.DCM', '.PNG')
            cv2.imwrite(imagePath, pixel_array_numpy)

        imageBackground = ImageWidget(imagePath, self)
        self.currentWidget = imageBackground
        self.setCentralWidget(self.currentWidget)

    def openFolder(self):
        folderPath = QFileDialog.getExistingDirectory(None, 'Select a folder', '', QFileDialog.ShowDirsOnly)
        print(folderPath)


if __name__ == "__main__":  # had to add this otherwise app crashed
    def run():
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        app = QApplication(sys.argv)
        Gui = MainWindow()
        sys.exit(app.exec_())
run()
