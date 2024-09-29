from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, 
    QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QToolBar,
    QStatusBar
)
from PyQt6.QtGui import QPixmap, QAction

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

    def buttonClicked(self):
        self.parent().buttonClicked(self.text)



class Home(QWidget):
    def __init__(self):
        super().__init__()

        self.outerContainer = QVBoxLayout()

        self.headerContainer = QHBoxLayout()
        label1 = QLabel("NihongoMax")
        font = label1.font()
        font.setPointSize(48)
        label1.setFont(font)
        label1.setAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignBottom)
        

        label2 = QLabel("JLPT preparation aide")
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
        # self.levelButtonContainer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        color_codes = ['ade9ff','adb0ff','ffadf1','ffcbad','d0ffad']
        self.buttons = [LevelButton(f"N{str(i)}",color_codes[i-1]) for i in range(1, 6)]


        for i in range(len(self.buttons)):
            # self.buttons[i].setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.levelButtonContainer.addWidget(self.buttons[i])

        # levelButtonVContainer = QVBoxLayout()
        # levelButtonVContainer.addLayout(self.levelButtonContainer)
        # levelButtonVContainer.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        self.outerContainer.addLayout(self.headerContainer)

        self.outerContainer.addLayout(self.levelButtonContainer)
        self.outerContainer.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        # self.outerContainer.addLayout(levelButtonVContainer)

        self.setLayout(self.outerContainer)

    def buttonClicked(self, text):
        # print(text)
        # if text == "N5":
        self.parent().displayLevelPage(text)

