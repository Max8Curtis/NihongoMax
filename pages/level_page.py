from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, 
    QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QToolBar,
    QStatusBar, QProgressBar, QGridLayout
)
from PyQt6.QtGui import QPixmap, QAction
from assets.styles.colors import Color

styles = "assets\styles\styles.css"


class ModeSelectButton(QWidget):
    def __init__(self, text):
        super().__init__()




class LevelPage(QWidget):
    def __init__(self, level):
        super().__init__()

        self.level = level
        self.colors = Color()
        self.buttonLabels = {1: "New lesson", 2: "Daily review", 3: "Translation quiz", 4: "Word match", 5: "Word fill"}
        self.buttons = []


        print(self.colors.get_level_color(self.level))

        self.outerContainer = QVBoxLayout()

        label1 = QLabel(self.level)
        label1.setMargin(200)
        font = label1.font()
        font.setPointSize(48)
        label1.setFont(font)
        label1.setStyleSheet(f"""
        background-color: #{self.colors.get_level_color(self.level)};
        color: #000000;
        font-family: Titillium;
        width: 300px;
        """)

        ## ------------------------- Progress bars

        self.progressBarContainer = QHBoxLayout()

        self.wordsProgressBar = QProgressBar()
        self.kanjiProgressBar = QProgressBar()
        self.grammarProgressBar = QProgressBar()
        with open("assets//styles//styles.css", "r") as f:
            style = f.read()
            self.wordsProgressBar.setStyleSheet(style)
            self.kanjiProgressBar.setStyleSheet(style)
            self.grammarProgressBar.setStyleSheet(style)
        
        self.wordsProgressBar.setMinimum(0)
        self.wordsProgressBar.setMaximum(100)
        self.wordsProgressBar.setValue(50)
        self.wordsProgressBar.setTextVisible(False)

        self.wordsLabel = QLabel("Words learnt", self)
        # self.wordsLearnCounter = QLabel(f"{words_learnt}/{words_count}")

        self.wordsProgressBarSubContainer = QHBoxLayout()

        self.wordsProgressBarSubContainer.addWidget(self.wordsLabel)
        self.wordsProgressBarContainer = QVBoxLayout()
        self.wordsProgressBarContainer.addLayout(self.wordsProgressBarSubContainer)
        self.wordsProgressBarContainer.addWidget(self.wordsProgressBar)

        self.kanjiProgressBar.setMinimum(0)
        self.kanjiProgressBar.setMaximum(100)
        self.kanjiProgressBar.setValue(50)
        self.kanjiProgressBar.setTextVisible(False)

        self.kanjiLabel = QLabel("Kanji learnt", self)
        # self.kanjiLearnCounter = QLabel(f"{kanji_learnt}/{kanji_count}")

        self.kanjiProgressBarSubContainer = QHBoxLayout()

        self.kanjiProgressBarSubContainer.addWidget(self.kanjiLabel)
        self.kanjiProgressBarContainer = QVBoxLayout()
        self.kanjiProgressBarContainer.addLayout(self.kanjiProgressBarSubContainer)
        self.kanjiProgressBarContainer.addWidget(self.kanjiProgressBar)

        self.grammarProgressBar.setMinimum(0)
        self.grammarProgressBar.setMaximum(100)
        self.grammarProgressBar.setValue(50)
        self.grammarProgressBar.setTextVisible(False)

        self.grammarLabel = QLabel("Grammar learnt", self)
        # self.grammarLearnCounter = QLabel(f"{grammar_learnt}/{grammar_count}")

        self.grammarProgressBarSubContainer = QHBoxLayout()

        self.grammarProgressBarSubContainer.addWidget(self.grammarLabel)
        
        self.grammarProgressBarContainer = QVBoxLayout()
        self.grammarProgressBarContainer.addLayout(self.grammarProgressBarSubContainer)
        self.grammarProgressBarContainer.addWidget(self.grammarProgressBar)

        self.progressBarContainer.addLayout(self.wordsProgressBarContainer)
        self.progressBarContainer.addLayout(self.kanjiProgressBarContainer)
        self.progressBarContainer.addLayout(self.grammarProgressBarContainer)

        ## ----------------------------- Buttons

        self.buttonLayout = QGridLayout()
        self.buttonLayout.setProperty("class", "buttonLayout")
        for i in range(len(list(self.buttonLabels.keys()))):
            buttonLabel = self.buttonLabels[i+1]
            self.buttons.append(QPushButton(buttonLabel, self))

        self.buttonLayout.addWidget(self.buttons[0], 0, 2, 1, 3)
        self.buttonLayout.addWidget(self.buttons[1], 2, 0, 1, 3)
        self.buttonLayout.addWidget(self.buttons[2], 2, 4, 1, 3)
        self.buttonLayout.addWidget(self.buttons[3], 4, 0, 1, 3)
        self.buttonLayout.addWidget(self.buttons[4], 4, 4, 1, 3)

        with open(styles, "r") as f:
            self.setStyleSheet(f.read())

        self.outerContainer.addWidget(label1)
        self.outerContainer.addLayout(self.progressBarContainer)
        self.outerContainer.addLayout(self.buttonLayout)

        self.outerContainer.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.setLayout(self.outerContainer)
