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
from pages.kana_race_page import KanaRacePage

# Only needed for access to command line arguments
import sys
import ctypes
import os

# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.
app = QApplication(sys.argv)


print(f"Operating system is: {os.name}")

if os.name == "nt":
    appID = 'microsoft.windows.nihongomax.v1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appID)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.page_stack = []
        self.homePage = Home()
        self.pushToStack({"page": type(self.homePage).__name__, "args": ()})
        self.homePage.setObjectName("home")
        self.setWindowIcon(QIcon(r'assets\images\1377200-m-1762661817.gif'))

        self.level_chosen = None
        self.levelMetaData = LevelMetaData()

        self.setWindowTitle("< Name pending >")
        self.setMinimumSize(QSize(1200, 700))
        self.label = QLabel()

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        self.initialiseToolbarButtons()

        self.setCentralWidget(self.homePage)

        self.setStatusBar(QStatusBar(self))

    def initialiseToolbarButtons(self):
        self.home_button_action = QAction(
            QIcon(r"assets//images//home.png"), "Home", self)
        self.home_button_action.setStatusTip("Return to home")
        self.home_button_action.triggered.connect(self.onHomeButtonClick)
        self.toolbar.addAction(self.home_button_action)

        self.toolbar.addSeparator()

        self.file_button_action = QAction("File", self)
        self.file_button_action.setStatusTip(
            "Application settings and preferences")
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

        self.toolbar.addSeparator()

        self.back_button_action = QAction(
            QIcon(r"assets//images//back_icon.jpg"), "Back", self)
        self.back_button_action.setStatusTip("Return to previous page")
        self.back_button_action.triggered.connect(self.onBackButtonClick)
        self.toolbar.addAction(self.back_button_action)

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

    def onBackButtonClick(self, s):
        print(self.page_stack)
        if len(self.page_stack) > 1:
            # page = self.page_stack[-2]["page"](self.page_stack[-2]["args"])
            def get_class(x): return globals()[x]
            page = get_class(
                self.page_stack[-2]["page"])(*self.page_stack[-2]["args"])
            self.setCentralWidget(page)
            self.page_stack = self.page_stack[:len(self.page_stack)-1]

    def pushToStack(self, page):
        print(type(page).__name__)
        self.page_stack.append(page)

    def displayLevelPage(self, *args):
        self.level_chosen = args[0]
        levelPage = LevelPage(self.level_chosen)
        self.pushToStack({"page": type(levelPage).__name__, "args": args})
        self.setCentralWidget(levelPage)

    def displayNewLessonPage(self, args=()):
        lessonPage = LessonPage(self.level_chosen)
        self.pushToStack({"page": type(lessonPage).__name__, "args": args})
        self.setCentralWidget(lessonPage)

    def displayWordMatchPage(self, args=()):
        wordMatchPage = WordMatchPage(self.level_chosen)
        self.pushToStack({"page": type(wordMatchPage).__name__, "args": args})
        self.setCentralWidget(wordMatchPage)

    def displayKanjiSpellPage(self, args=()):
        kanjiSpellPage = KanjiSpellPage(self.level_chosen)
        self.pushToStack({"page": type(kanjiSpellPage).__name__, "args": args})
        self.setCentralWidget(kanjiSpellPage)

    def displayKanaRacePage(self, args=()):
        kanaRacePage = KanaRacePage(self.level_chosen)
        self.pushToStack({"page": type(kanaRacePage).__name__, "args": args})
        self.setCentralWidget(kanaRacePage)


window = MainWindow()
window.show()

styles = "assets\styles\styles.css"
colors = {
    "N1color": '#ade9ff',
    "N2color": '#adb0ff',
    "N3color": '#ffadf1',
    "N4color": '#ffcbad',
    "N5color": '#62bb96'
}

with open(styles, 'r') as f:
    styling = f.read()
    for i in list(colors.keys()):
        styling = styling.replace(i, colors[i])
    window.setStyleSheet(styling)

# Start the event loop
app.exec()
