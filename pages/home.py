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
    def __init__(self, text, bgroundColor):
        super().__init__()

        self.text = text
        self.button = QPushButton(text, self)
        self.button.setStyleSheet(f"""
        background-color: #{bgroundColor};
        color: #000000;
        font-family: Titillium;
        font-size: 30px;
        margin-right: 5px;
        margin-left: 5px;
        """)
        
        self.button.setMinimumHeight(150)
        self.button.setMinimumWidth(150)

        self.button.clicked.connect(self.buttonClicked)
        self.button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))


    def buttonClicked(self):
        self.parent().displayLevelPage(self.text)



class Home(QWidget):
    def __init__(self):
        super().__init__()

        self.outerContainer = QVBoxLayout()
        self.colors = Color()

        self.headerContainer = QHBoxLayout()
        label1 = QLabel("NihongoMax")
        font = label1.font()
        font.setPointSize(48)
        label1.setFont(font)
        label1.setAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignBottom)
        

        label2 = QLabel("JLPT preparation tool")
        font = label2.font()
        font.setPointSize(26)
        label2.setFont(font)
        label2.setAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)

        self.titleContainer = QVBoxLayout()
        self.titleContainer.addWidget(label1)
        self.titleContainer.addWidget(label2)


        image1 = QLabel(self)
        # pixmap = QPixmap(r"assets//images//zeimusu-kanji-e-3120189007-resized.png")
        pixmap = QPixmap(r"assets//images//1377200-m-1762661817.gif")
        image1.setPixmap(pixmap)
        image1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        image2 = QLabel(self)
        pixmap = QPixmap(r"assets//images//1200px-Flag_of_Japan.svg-773342002-resized.png")
        image2.setPixmap(pixmap)
        image2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        
        self.headerContainer.addWidget(image1)
        self.headerContainer.addLayout(self.titleContainer)
        self.headerContainer.addWidget(image2)
        self.headerContainer.setSpacing(20)

        self.levelButtonContainer = QHBoxLayout()
    
        self.buttons = [LevelButton(f"N{str(i)}",self.colors.get_level_color(f"N{str(i)}")) for i in range(1, 6)]

        for i in range(len(self.buttons)):
            self.levelButtonContainer.addWidget(self.buttons[i])

        self.outerContainer.addLayout(self.headerContainer)

        self.outerContainer.addLayout(self.levelButtonContainer)
        self.outerContainer.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        with open(styles, 'r') as f:
            self.setStyleSheet(f.read())

        self.setLayout(self.outerContainer)


    def displayLevelPage(self, text):
        self.parent().displayLevelPage(text)

    def displayNewLessonPage(self):
        self.parent().displayNewLessonPage()

    def displayWordMatchPage(self):
        self.parent().displayWordMatchPage()



