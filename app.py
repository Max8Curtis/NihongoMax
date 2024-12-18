from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, 
    QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QToolBar,
    QStatusBar, QStackedLayout
)
from PyQt6.QtGui import QPixmap, QAction, QIcon
from pages.home import Home
from pages.level_page import LevelPage
from assets.data import LevelMetaData
from pages.lesson_page import LessonPage
from pages.word_match_page import WordMatchPage
from pages.kanji_spell_page import KanjiSpellPage

# Only needed for access to command line arguments
import sys

# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.
app = QApplication(sys.argv)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.homePage = Home()

        self.level_chosen = None
        self.levelMetaData = LevelMetaData()

        self.setWindowTitle("NihongoMax")
        self.setMinimumSize(QSize(1200,700))
        self.label = QLabel()

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        self.initialiseToolbarButtons()

        self.setCentralWidget(self.homePage)

        self.setStatusBar(QStatusBar(self))

    def initialiseToolbarButtons(self):
        self.home_button_action = QAction(QIcon(r"assets//images//home.png"), "Home", self)
        self.home_button_action.setStatusTip("Return to home")
        self.home_button_action.triggered.connect(self.onHomeButtonClick)
        self.toolbar.addAction(self.home_button_action)

        self.file_button_action = QAction("File", self)
        self.file_button_action.setStatusTip("Application settings and preferences")
        self.file_button_action.triggered.connect(self.onFileButtonClick)
        self.toolbar.addAction(self.file_button_action)

        self.words_button_action = QAction("Words", self)
        self.words_button_action.setStatusTip("View vocabulary lists")
        self.words_button_action.triggered.connect(self.onWordsButtonClick)
        self.toolbar.addAction(self.words_button_action)

        self.kanji_button_action = QAction("Kanji", self)
        self.kanji_button_action.setStatusTip("View kanji lists")
        self.kanji_button_action.triggered.connect(self.onKanjiButtonClick)
        self.toolbar.addAction(self.kanji_button_action)

        self.grammar_button_action = QAction("Grammar", self)
        self.grammar_button_action.setStatusTip("View grammar lists")
        self.grammar_button_action.triggered.connect(self.onGrammarButtonClick)
        self.toolbar.addAction(self.grammar_button_action)

    def onHomeButtonClick(self, s):
        print("click", s)
        self.homePage = Home()
        self.setCentralWidget(self.homePage)
        # self.pageLayout.setCurrentIndex(0)

    def onFileButtonClick(self, s):
        print("click", s)

    def onWordsButtonClick(self, s):
        print("click", s)

    def onKanjiButtonClick(self, s):
        print("click", s)

    def onGrammarButtonClick(self, s):
        print("click", s)

    def displayLevelPage(self, level):
        self.level_chosen = level
        levelPage = LevelPage(level)
        self.setCentralWidget(levelPage)

    def displayNewLessonPage(self):
        lessonPage = LessonPage(self.level_chosen)
        self.setCentralWidget(lessonPage)

    def displayWordMatchPage(self):
        wordMatchPage = WordMatchPage(self.level_chosen)
        self.setCentralWidget(wordMatchPage)

    def displayKanjiSpellPage(self):
        kanjiSpellPage = KanjiSpellPage(self.level_chosen)
        self.setCentralWidget(kanjiSpellPage)

window = MainWindow()
window.show()


# Start the event loop
app.exec()
