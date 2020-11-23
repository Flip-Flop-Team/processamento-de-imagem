import sys
import os
import numpy
import time
from PyQt5.QtCore import QCoreApplication, Qt, QT_TR_NOOP as tr
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QFileDialog, QAction, QMessageBox
from widgets.imageWidget import ImageWidget
import signal
import pydicom as dicom
import cv2
import sklearn
from random import shuffle
from skimage.feature import greycomatrix, greycoprops
from skimage.measure import shannon_entropy, moments_hu
from PIL import Image

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
        actionMenu.addAction(self.createTopMenuAction('Show info', '', 'Show informations', self.showImagesInfo))
        actionMenu.addAction(self.createTopMenuAction('Show info selected image', '', 'Show informations selected image', self.showImagesInfoUniqueImage))

        trainingMenu.addAction(self.createTopMenuAction('Calculate characteristics', '', 'Calculate characteristics from images', self.calculate))
        trainingMenu.addAction(self.createTopMenuAction('Train', 'Ctrl+T', 'Train using images', self.train))
        trainingMenu.addAction(self.createTopMenuAction('Classificate', '', 'Classificate last 25%', self.classificate))
        trainingMenu.addAction(self.createTopMenuAction('Classificate selected area', '', 'Classificate image', self.cropImageAndSave))
        trainingMenu.addAction(self.createTopMenuAction('Homogeneidade', '', 'Use homogeneity', self.useHomogeneity, True))
        trainingMenu.addAction(self.createTopMenuAction('Entropy', '', 'Use entropy', self.useEntropy, True))
        trainingMenu.addAction(self.createTopMenuAction('Energy', '', 'Use energy', self.useEnergy, True))
        trainingMenu.addAction(self.createTopMenuAction('Constrast', '', 'Use contrast', self.useContrast, True))

    def useHomogeneity(self, checked):
        self.characteristics['homogeneity'] = checked
    def useEntropy(self, checked):
        self.characteristics['entropy'] = checked
    def useEnergy(self, checked):
        self.characteristics['energy'] = checked
    def useContrast(self, checked):
        self.characteristics['contrast'] = checked
    def unselect(self):
        self.currentWidget.drawReact = False
        self.currentWidget.label.setPixmap(self.currentWidget.zoomedPixmap)

    def zoomImage(self):
        if hasattr(self, 'currentWidget'):
            size = self.currentWidget.originalPixmap.size()
            self.currentWidget.zoomFunction(1)
        else:
            self.showErrorMessage('You need to open a image first')

    def showImagesInfo(self):
        acuracia = sum(self.tabela[i][i]for i in range(4))/100
        especificidade = 1 - sum(25 - self.tabela[i][i]for i in range(4))/300
        message = "Matriz de confusão\n"
        for i in self.tabela:
            for j in i:
                message += str(j)
                message += '  '
            message += '\n'
        message += 'Acuracia: {} \n'.format(acuracia)
        message += 'Especifidade: {} \n'.format(especificidade)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Info")
        msg.setInformativeText(message)
        msg.setWindowTitle("Informações")
        msg.exec_()

    def showImagesInfoUniqueImage(self):
        if not hasattr(self, 'characteristicsUniqueImage'):
            showErrorMessage('É necessário classificar a imagem unica')
            return
        message = ""
        message += 'Homogeinedade: {} \n'.format(str(round(self.characteristicsUniqueImage['homogeneity'][0], 3)))
        message += 'Contraste: {} \n'.format(str(round(self.characteristicsUniqueImage['contrast'][0], 3)))
        message += 'Energia: {} \n'.format(str(round(self.characteristicsUniqueImage['energy'][0], 3)))
        message += 'Entropia: {} \n'.format(str(round(self.characteristicsUniqueImage['entropy'], 3)))
        message += 'Hu: {} \n'.format(str(round(self.characteristicsUniqueImage['hu_moments'][0], 3)))
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Info")
        msg.setInformativeText(message)
        msg.setWindowTitle("Informações")
        msg.exec_()

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
            ds = dicom.dcmread(imagePath)
            pixel_array_numpy = ds.pixel_array
            imagePath = imagePath.replace('.DCM', '.PNG')
            cv2.imwrite(imagePath, pixel_array_numpy)

        imageBackground = ImageWidget(imagePath, self)
        self.imagePath = imagePath
        self.currentWidget = imageBackground
        self.setCentralWidget(self.currentWidget)

    def cropImageAndSave(self):
        if not (hasattr(self, 'currentWidget') and hasattr(self.currentWidget, 'p1x')):
            self.showErrorMessage('É necessário selecionar uma área')
            return
        im = Image.open(self.imagePath)
        im1 = im.crop((self.currentWidget.p1x, self.currentWidget.p1y, self.currentWidget.p2x, self.currentWidget.p2y)).save('cropped.png')
        self.classicateOneImage()

    def openFolder(self):
        try:
            folderPath = QFileDialog.getExistingDirectory(None, 'Select a folder', '', QFileDialog.ShowDirsOnly)
            self.images_dictionary = {1: [], 2: [], 3: [], 4: []}  
            for item in range(1,5):
                images = os.listdir(folderPath + '/{}'.format(item))
                image_key = 0
                for image in images:
                    grey_image = cv2.imread('{}/{}/{}'.format(folderPath, item, image), 0)
                    self.images_dictionary[item].append({
                        'id': image_key,
                        'image': grey_image
                    })
                    image_key += 1
            self.showSuccessMessage('Diretório lido com sucesso')
        except:
           self.showErrorMessage('Erro ao ler o diretorio, tente novamente')

    def calculate(self):
        """
        Calculate images caracteristics and put them in self.images_caracteristics with the structure:
        {
            1: [], <- images from folder 1
            2: [], <- images from folder 2
            3: [], <- images from folder 3
            4: []  <- images from folder 4
        }
        The "[]" have 100 dictionaries with id, and the caracteristics
        homogeinity => [] with 5 positions
        entropy => number
        energy => [] with 5 positions
        contrast => [] with 5 positions
        hu_moments => [] with 7 positions
        """
        if self.characteristics == {}:
            self.showErrorMessage('Nenhuma caracteristica foi selecionada')
            return
        
        if not hasattr(self, 'images_dictionary'):
            self.showErrorMessage('Diretório de imagens não selecionado')
            return
        try:
            self.images_characteristics = {1: [], 2: [], 3: [], 4: []} # 1: homogeneity, 2: entropy, 3: energy, 4: contrast 
            print("Calculating caracteristics")
            for item in range(1, 5):
                for element in self.images_dictionary[item]:
                    image = numpy.array((element['image']/8), 'int')
                    comatrix = greycomatrix(image,[1,2,4,8,16], [0, numpy.pi/4, numpy.pi/2,  3*numpy.pi/4], levels=32, normed=True, symmetric=True)
                    characteristics = {'id': element['id']}
                    if 'homogeneity' in self.characteristics and self.characteristics['homogeneity']:
                        characteristics['homogeneity'] = [sum(i) for i in greycoprops(comatrix, 'homogeneity')]
                    if 'entropy' in self.characteristics and self.characteristics['entropy']:
                        characteristics['entropy'] = shannon_entropy(image)
                    if 'energy' in self.characteristics and self.characteristics['energy']:
                        characteristics['energy'] = [sum(i) for i in greycoprops(comatrix, 'energy')]
                    if 'contrast' in self.characteristics and self.characteristics['contrast']:
                        characteristics['contrast'] =[sum(i) for i in greycoprops(comatrix, 'contrast')]
                    characteristics['hu_moments'] = list(moments_hu(image))
                    self.images_characteristics[item].append(characteristics)
            self.showSuccessMessage('Calculo realizado com sucesso')
        except Exception as err:
            print(err)
            self.showErrorMessage('Erro ao calcular, tente novamente')

    def calcAverage(self, imagens_treinamento):
        '''
        As médias de todas as caracteristicas são feitas, exemplo:
        em avg[1]['homogeneity'] temos uma lista de 5 posições onde a
        primeira é a média da primeira posição de homogeinidade das
        imagens da pasta 1
        '''
        avg = {}
        caracteristics = ['homogeneity', 'entropy', 'energy', 'contrast', 'hu_moments']
        for item in range(1,5):
            avg[item] = {}
            for c in caracteristics:
                if c not in imagens_treinamento[item][0]:
                    continue
                if c == 'entropy': 
                    avg[item][c] = sum([j[c] for j in imagens_treinamento[item]])/75
                else:
                    avg[item][c] = [sum(i)/75 for i in zip(*[j[c] for j in imagens_treinamento[item]])]

        return avg

    def centerInAvg(self, imagens_treinamento, average):
        '''
        Diminuir todos os valores pela media do valor gerado em self.average correspondente
        '''
        caracteristics = ['homogeneity', 'entropy', 'energy', 'contrast', 'hu_moments']
        for item in range(1,5):
            for i in range(75):
                for c in caracteristics:
                    if c not in imagens_treinamento[item][0]:
                        continue
                    if c == 'entropy':
                        imagens_treinamento[item][i][c] = imagens_treinamento[item][i][c] - average[item][c]
                    else:
                        imagens_treinamento[item][i][c] = numpy.subtract(imagens_treinamento[item][i][c], average[item][c])
        return imagens_treinamento

    def covariance(self, imagens_treinamento):
        covariance = [[],[],[],[]]
        caracteristics = {'homogeneity': 5, 'entropy': 1, 'energy': 5, 'contrast':5, 'hu_moments': 7}
        for item in range(1,5):
            for c in caracteristics:
                if c not in imagens_treinamento[item][0]:
                    continue
                if caracteristics[c] > 1:
                    for j in range(caracteristics[c]):
                        covariance[item-1].append([i[c][j] for i in imagens_treinamento[item]])
                else:
                    covariance[item-1].append([i[c] for i in imagens_treinamento[item]])

        matrizesCovariancia = []
        self.matrizesCovarianciaInversas = []
        for item in range(4):
            matrizesCovariancia.append(numpy.cov([list(i) for i in covariance[item]]))
            self.matrizesCovarianciaInversas.append(numpy.linalg.inv(matrizesCovariancia[item]))


    def train(self):
        tic = time.perf_counter()
        if not hasattr(self, 'images_characteristics'):
            self.showErrorMessage('Você precisa calcular as caracteristicas antes de realizar o treinamento')
            return
        random_list = list(range(0, 100))
        shuffle(random_list)
        imagens_treinamento = {1: [], 2: [], 3: [], 4: []}
        self.imagens_classificacao = {1: [], 2: [], 3: [], 4: []}

        for item in range(1,5):
            for index in range(0, 75):
                imagens_treinamento[item].append(self.images_characteristics[item][random_list[index]])
            for index in range(75,100):
                self.imagens_classificacao[item].append(self.images_characteristics[item][random_list[index]])
        self.average = self.calcAverage(imagens_treinamento)
        imagens_treinamento = self.centerInAvg(imagens_treinamento, self.average)
        self.covariance(imagens_treinamento)
        toc = time.perf_counter()
        self.showSuccessMessage(f"Treino concluído com sucesso {toc-tic:0.4f} seconds")

    def classicateOneImage(self):
        tic = time.perf_counter()
        if not (hasattr(self, 'currentWidget') and hasattr(self.currentWidget, 'p1x')):
            self.showErrorMessage('É necessário selecionar uma área')
            return
        im = cv2.imread('cropped.png', 0)
        image = numpy.array((im/8), 'int')
        comatrix = greycomatrix(image,[1,2,4,8,16], [0, numpy.pi/4, numpy.pi/2,  3*numpy.pi/4], levels=32, normed=True, symmetric=True)
        characteristics = {}
        if 'homogeneity' in self.characteristics and self.characteristics['homogeneity']:
            characteristics['homogeneity'] = [sum(i) for i in greycoprops(comatrix, 'homogeneity')]
        if 'entropy' in self.characteristics and self.characteristics['entropy']:
            characteristics['entropy'] = shannon_entropy(image)
        if 'energy' in self.characteristics and self.characteristics['energy']:
            characteristics['energy'] = [sum(i) for i in greycoprops(comatrix, 'energy')]
        if 'contrast' in self.characteristics and self.characteristics['contrast']:
            characteristics['contrast'] =[sum(i) for i in greycoprops(comatrix, 'contrast')]
        characteristics['hu_moments'] = list(moments_hu(image))
        self.characteristicsUniqueImage = characteristics
        caracteristics = ['homogeneity', 'entropy', 'energy', 'contrast', 'hu_moments']
        B = {}
        for item in range(1,5):
            B[item] = []
            for c in caracteristics:
                if c not in self.average[item]:
                    continue
                if c == 'entropy':
                    B[item].append(self.average[item][c])
                else:
                    B[item] += list(self.average[item][c])
        A = []
        for c in caracteristics:
            if c not in characteristics:
                continue
            if c == 'entropy':
                A.append(characteristics[c])
            else:
                A += list(characteristics[c])

        menor = 0
        menorValor = -1
        for item3 in range(1,5):
            dif = numpy.subtract(A,B[item3])
            dist = numpy.dot(numpy.dot(numpy.array(dif).T, self.matrizesCovarianciaInversas[item3-1]), numpy.array(dif))
            if(menorValor == -1):
                menorValor = dist
            elif(dist < menorValor):
                menor = item3-1
                menorValor = dist
                
        self.imageClassification = menor
        toc = time.perf_counter()
        self.showSuccessMessage(f"Classificação concluído com sucesso {toc-tic:0.4f} seconds")

        


    def classificate(self):
        tic = time.perf_counter()
        if not hasattr(self, 'matrizesCovarianciaInversas'):
            self.showErrorMessage('Você precisa treinar antes de classificar')
            return
        caracteristics = ['homogeneity', 'entropy', 'energy', 'contrast', 'hu_moments']
        B = {}
        tabela = [[0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]]
        for item in range(1,5):
            B[item] = []
            for c in caracteristics:
                if c not in self.average[item]:
                    continue
                if c == 'entropy':
                    B[item].append(self.average[item][c])
                else:
                    B[item] += list(self.average[item][c])
        
        for item in range(1,5):
            for image in self.imagens_classificacao[item]:
                A = []
                for c in caracteristics:
                    if c not in image:
                        continue
                    if c == 'entropy':
                        A.append(image[c])
                    else:
                        A += list(image[c])

                menor = 0
                menorValor = -1
                for item3 in range(1,5):
                    dif = numpy.subtract(A,B[item3])
                    dist = numpy.dot(numpy.dot(numpy.array(dif).T, self.matrizesCovarianciaInversas[item3-1]), numpy.array(dif))
                    if(menorValor == -1):
                        menorValor = dist
                    elif(dist < menorValor):
                        menor = item3-1
                        menorValor = dist
                # A tabela no diretorio item-1 classificou como menor a imagem
                tabela[item - 1][menor] += 1

        self.tabela = tabela
        toc = time.perf_counter()
        self.showSuccessMessage(f"Treino concluído com sucesso {toc-tic:0.4f} seconds")
                
        
if __name__ == "__main__":  # had to add this otherwise app crashed
    def run():
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        app = QApplication(sys.argv)
        Gui = MainWindow()
        sys.exit(app.exec_())
run()
