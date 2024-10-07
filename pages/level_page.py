from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, 
    QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QToolBar,
    QStatusBar, QProgressBar, QGridLayout
)
from PyQt6.QtGui import QPixmap, QAction, QCursor
from PyQt6 import QtCore
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
        print(self.level)


        print(self.colors.get_level_color(self.level))

        self.outerContainer = QVBoxLayout()
        # self.outerContainer.setProperty("class", "outerContainer")


        labelLayout = QHBoxLayout()
        labelLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label1 = QLabel(self.level)
        # label1.setProperty("class", "levelPageTitle")
        # label1.setMargin(200)
        font = label1.font()
        font.setPointSize(60)
        label1.setFont(font)
        label1.setStyleSheet(f"""
        color: #{self.colors.get_level_color(self.level)};
        font-family: Titillium;
       
        width: 300px;
        height: 100px;

        """)

        labelLayout.addWidget(label1)

        ## ------------------------- Progress bars

        self.progressBarContainer = QHBoxLayout()

        self.wordsProgressBar = QProgressBar()
        self.kanjiProgressBar = QProgressBar()
        self.grammarProgressBar = QProgressBar()
        # with open("assets//styles//styles.css", "r") as f:
        #     style = f.read()
        #     self.wordsProgressBar.setStyleSheet(style)
        #     self.kanjiProgressBar.setStyleSheet(style)
        #     self.grammarProgressBar.setStyleSheet(style)
        
        self.wordsProgressBar.setMinimum(0)
        self.wordsProgressBar.setMaximum(100)
        self.wordsProgressBar.setValue(50)
        self.wordsProgressBar.setTextVisible(False)

        self.wordsLabel = QLabel("Words learnt", self)
        words_learnt = 150
        words_count = 1000
        self.wordsLearnCounter = QLabel(f"{words_learnt}/{words_count}")

        self.wordsProgressBarSubContainer = QHBoxLayout()

        dudWordsContainer1 = QHBoxLayout()
        dudWordsContainer1.addWidget(self.wordsLabel)
        dudWordsContainer1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        dudWordsContainer2 = QHBoxLayout()
        dudWordsContainer2.addWidget(self.wordsLearnCounter)
        dudWordsContainer2.setAlignment(Qt.AlignmentFlag.AlignRight)

        # self.wordsProgressBarSubContainer.addWidget(self.wordsLabel)
        # self.wordsProgressBarSubContainer.addWidget(self.wordsLearnCounter)
        self.wordsProgressBarSubContainer.addLayout(dudWordsContainer1)
        self.wordsProgressBarSubContainer.addLayout(dudWordsContainer2)
        # self.wordsProgressBarSubContainer.setSpacing(300)
        self.wordsProgressBarContainer = QVBoxLayout()
        self.wordsProgressBarContainer.addLayout(self.wordsProgressBarSubContainer)
        self.wordsProgressBarContainer.addWidget(self.wordsProgressBar)
        self.wordsProgressBarContainer.setContentsMargins(0,30,0,60)

        self.kanjiProgressBar.setMinimum(0)
        self.kanjiProgressBar.setMaximum(100)
        self.kanjiProgressBar.setValue(50)
        self.kanjiProgressBar.setTextVisible(False)

        self.kanjiLabel = QLabel("Kanji learnt", self)
        kanji_learnt = 100
        kanji_count = 500
        self.kanjiLearnCounter = QLabel(f"{kanji_learnt}/{kanji_count}")

        self.kanjiProgressBarSubContainer = QHBoxLayout()

        dudKanjiContainer1 = QHBoxLayout()
        dudKanjiContainer1.addWidget(self.kanjiLabel)
        dudKanjiContainer1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        dudKanjiContainer2 = QHBoxLayout()
        dudKanjiContainer2.addWidget(self.kanjiLearnCounter)
        dudKanjiContainer2.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.kanjiProgressBarSubContainer.addLayout(dudKanjiContainer1)
        self.kanjiProgressBarSubContainer.addLayout(dudKanjiContainer2)
        # self.kanjiProgressBarSubContainer.setSpacing(300)
        self.kanjiProgressBarContainer = QVBoxLayout()
        self.kanjiProgressBarContainer.addLayout(self.kanjiProgressBarSubContainer)
        self.kanjiProgressBarContainer.addWidget(self.kanjiProgressBar)
        self.kanjiProgressBarContainer.setContentsMargins(0,30,0,60)

        self.grammarProgressBar.setMinimum(0)
        self.grammarProgressBar.setMaximum(100)
        self.grammarProgressBar.setValue(50)
        self.grammarProgressBar.setTextVisible(False)

        self.grammarLabel = QLabel("Grammar learnt", self)
        grammar_learnt = 50
        grammar_count = 175
        self.grammarLearnCounter = QLabel(f"{grammar_learnt}/{grammar_count}")

        self.grammarProgressBarSubContainer = QHBoxLayout()

        dudGrammarContainer1 = QHBoxLayout()
        dudGrammarContainer1.addWidget(self.grammarLabel)
        dudGrammarContainer1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        dudGrammarContainer2 = QHBoxLayout()
        dudGrammarContainer2.addWidget(self.grammarLearnCounter)
        dudGrammarContainer2.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.grammarProgressBarSubContainer.addLayout(dudGrammarContainer1)
        self.grammarProgressBarSubContainer.addLayout(dudGrammarContainer2)
        # self.grammarProgressBarSubContainer.setSpacing(300)
        
        self.grammarProgressBarContainer = QVBoxLayout()


        self.grammarProgressBarContainer.addLayout(self.grammarProgressBarSubContainer)
        self.grammarProgressBarContainer.addWidget(self.grammarProgressBar)
        # self.grammarProgressBarContainer.setSpacing(0)
        self.grammarProgressBarContainer.setContentsMargins(0,30,0,60)

        self.progressBarContainer.addLayout(self.wordsProgressBarContainer)
        self.progressBarContainer.addLayout(self.kanjiProgressBarContainer)
        self.progressBarContainer.addLayout(self.grammarProgressBarContainer)

        ## ----------------------------- Buttons

        self.buttonLayout = QGridLayout()
        self.buttonLayout.setProperty("class", "buttonLayout")
        for i in range(len(list(self.buttonLabels.keys()))):
            buttonLabel = self.buttonLabels[i+1]
            self.buttons.append(QPushButton(buttonLabel, self))
            self.buttons[i].setProperty("class", "levelButton")
            self.buttons[i].setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

        self.buttonLayout.addWidget(self.buttons[0], 0, 2, 1, 3)
        self.buttonLayout.addWidget(self.buttons[1], 2, 0, 1, 3)
        self.buttonLayout.addWidget(self.buttons[2], 2, 4, 1, 3)
        self.buttonLayout.addWidget(self.buttons[3], 4, 0, 1, 3)
        self.buttonLayout.addWidget(self.buttons[4], 4, 4, 1, 3)



        # self.outerContainer.addWidget(label1)
        self.outerContainer.addLayout(labelLayout)
        self.outerContainer.addLayout(self.progressBarContainer)
        self.outerContainer.addLayout(self.buttonLayout)

        self.outerContainer.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        with open(styles, "r") as f:
            self.setStyleSheet(f.read())

        dudContainer = QHBoxLayout()
        # dudContainer.setStyleSheet("""padding:20px;""")
        dudContainer.setContentsMargins(90,50,90,50)
        dudContainer.addLayout(self.outerContainer)
        # self.setLayout(self.outerContainer)
        self.setLayout(dudContainer)
        
