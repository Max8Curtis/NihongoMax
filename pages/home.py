from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, 
    QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QToolBar,
    QStatusBar
)
from PyQt6.QtGui import QPixmap, QAction, QCursor
from PyQt6 import QtCore
from assets.styles.colors import Color

styles = "assets\styles\styles.css"

class LevelButton(QWidget):
    def __init__(self, text):
        super().__init__()

        self.text = text
        self.button = QPushButton(text, self)
        
        self.button.setObjectName("levelButton"+text)
            
        # self.button.setMinimumHeight(150)
        # self.button.setMinimumWidth(150)

        self.button.clicked.connect(self.buttonClicked)
        self.button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

    def buttonClicked(self):
        self.parent().parent().displayLevelPage(self.text)



class Home(QWidget):
    def __init__(self):
        super().__init__()

        # self.setProperty("class", "home")
        

        self.outerContainer = QVBoxLayout()
        self.colors = Color()

        self.headerContainer = QHBoxLayout()
        label1 = QLabel("NihongoMax")
        label1.setObjectName("applicationTitle")
        label1.setAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignBottom)
        

        label2 = QLabel("JLPT preparation tool")
        label2.setObjectName("applicationSubTitle")
        label2.setAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)

        self.titleContainer = QVBoxLayout()
        self.titleContainer.addWidget(label1)
        self.titleContainer.addWidget(label2)

        # image1 = QLabel(self)
        # pixmap = QPixmap(r"assets//images//1377200-m-1762661817.gif")
        # image1.setPixmap(pixmap)
        # image1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # image2 = QLabel(self)
        # pixmap = QPixmap(r"assets//images//1200px-Flag_of_Japan.svg-773342002-resized.png")
        # image2.setPixmap(pixmap)
        # image2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.headerContainer.addLayout(self.titleContainer)

        self.levelButtonContainer = QHBoxLayout()

        widget = QWidget()
        widget.setObjectName("levelButtonsContainerDummy")
    
        self.buttons = [LevelButton(f"N{str(i)}") for i in range(1, 6)]

        for i in range(len(self.buttons)):
            self.levelButtonContainer.addWidget(self.buttons[i])

        widget.setLayout(self.levelButtonContainer)

        self.outerContainer.addStretch(1)
        self.outerContainer.addLayout(self.headerContainer)
        self.outerContainer.addStretch(1)
        self.outerContainer.addWidget(widget)
        self.outerContainer.addStretch(1)

        self.outerContainer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.outerContainer)

    def displayLevelPage(self, text):
        self.parent().displayLevelPage(text)

    def displayNewLessonPage(self):
        self.parent().displayNewLessonPage()

    def displayWordMatchPage(self):
        self.parent().displayWordMatchPage()

    def displayKanjiSpell(self):
        self.parent().displayKanjiSpellPage()

    def displayKanaRacePage(self):
        self.parent().displayKanaRacePage()


