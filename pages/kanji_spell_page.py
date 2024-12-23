from database import Database
from bs4 import BeautifulSoup
import requests
import shutil
import random
from romaji.convert import Convert
import time

from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, 
    QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QToolBar,
    QStatusBar, QStackedLayout, QGridLayout, QCheckBox, QMenu,
    QDialog, QDialogButtonBox, QComboBox, QScrollArea, QListWidget,
    QAbstractButton, QListWidgetItem, QRadioButton, QSpinBox
)
from PyQt6.QtGui import QPixmap, QAction, QCursor, QPainter
from PyQt6 import QtCore
from assets.styles.colors import Color
from assets.widgets import SelectWordField, StartButton
from assets.tools import Tools
tools = Tools()

styles = "assets\styles\styles.css"

class PlayArea(QWidget):
    def __init__(self, words):
        super().__init__()
        self.words = words
        self.started = False
        self.words['selected'] = [False for i in range(self.words.shape[0])]
        self.answer_submitted = False
        self.current = 0
        self.display_en = False
        self.kanji_fontsize = 50
        self.english_fontsize = 42
        self.answer_fontsize = 32
        self.prev_input_text = ""
        self.input_text = ""
        self.convert = Convert()

        self.container = QHBoxLayout()
    
        self.options_container = QHBoxLayout()
        self.options_grid = QGridLayout()
        self.options_grid.setColumnMinimumWidth(2, 100)
        self.options_grid.setColumnStretch(3, 1)
        self.options_grid.setColumnStretch(5, 1)
        self.options_grid.setColumnStretch(0, 1)
        self.options_grid.setRowStretch(0,1)
        self.options_grid.setRowStretch(4,1)

        self.options_label = QLabel('Options:')
        self.setFontSize(self.options_label, 20)
        self.options_container.addWidget(self.options_label)

        self.spin_box = QSpinBox(self)
        self.spin_box.setRange(0, 600)  # Set the range of values
        self.spin_box.setValue(1)
        self.loop_radio = QRadioButton('Loop', self)
        self.loop_radio.setChecked(True)
        self.options_grid.addWidget(self.loop_radio, 1, 1)   
        self.timer_radio = QRadioButton('Timer (seconds)', self)
        self.timer_radio.toggled.connect(self.timerRadioToggled)
        self.spin_box.setEnabled(False)
        self.options_grid.addWidget(self.timer_radio, 2, 1)   
        self.options_grid.addWidget(self.spin_box, 2, 2)
        self.toggle_english_checkbox = QCheckBox('Display English')
        self.toggle_english_checkbox.stateChanged.connect(self.englishToggled)
        self.options_grid.addWidget(self.toggle_english_checkbox, 3, 1)

        self.options_container.addLayout(self.options_grid)

        self.start_button = StartButton()
        self.options_grid.addWidget(self.start_button, 2, 4)

        self.options_play_area_container = QVBoxLayout()

        self.options_play_area_container.addLayout(self.options_container)

        self.play_area_container = QGridLayout()
        self.play_area_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.kanji_label = QLabel('漢字')
        self.setFontSize(self.kanji_label, self.kanji_fontsize)

        self.english_label = QLabel('')
        self.setFontSize(self.english_label, self.english_fontsize)

        self.answer_label = QLabel('')
        self.setFontSize(self.answer_label, self.answer_fontsize)

        self.answer_input = QLineEdit()
        self.answer_input.setMaxLength(15)
        self.answer_input.setMinimumWidth(200)
        self.answer_input.editingFinished.connect(self.enterBtnPressed)
        self.answer_input.setProperty("class", "answerInput")
        self.answer_input.setAlignment(Qt.AlignmentFlag.AlignCenter)              # <-----
        self.answer_input.textEdited.connect(self.textInputted)
        self.setFontSize(self.answer_input, 14)

        self.enter_button = QPushButton()
        self.enter_button.setMinimumHeight(60)
        self.enter_button.setMinimumWidth(60)
        self.enter_button_layout = QHBoxLayout()
        self.enter_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.enter_label = QLabel('Enter')
        self.setFontSize(self.enter_label, 14)
        self.enter_button_layout.addWidget(self.enter_label)
        self.enter_button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.enter_button.setProperty("class", "button")
        self.enter_button.setLayout(self.enter_button_layout)
        self.enter_button.clicked.connect(self.enterBtnPressed)
        
        self.play_area_container.addWidget(self.kanji_label, 0, 1, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.play_area_container.addWidget(self.english_label, 1, 1, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.play_area_container.addWidget(self.answer_label, 2, 1, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.play_area_container.addWidget(self.answer_input, 4, 1, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.play_area_container.addWidget(self.enter_button, 4, 3, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        self.play_area_container.setColumnStretch(0,1)
        self.play_area_container.setColumnStretch(4,1)
        self.play_area_container.setRowStretch(3,1)
        self.play_area_container.setContentsMargins(0,50,0,0)

        self.options_play_area_container.addLayout(self.play_area_container)
        self.options_play_area_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.options_play_area_container.addStretch(1)

        self.select_words_field = SelectWordField(parent=self, words=self.words)

        self.container.addLayout(self.options_play_area_container)
        self.container.addWidget(self.select_words_field)

        with open(styles, "r") as f:
            self.setStyleSheet(f.read())

        self.setLayout(self.container) 

    def startBtnPressed(self):
        chosen_word_ids = self.select_words_field.getChosenWords()
        self.chosen_words = self.words[self.words['id'].isin(chosen_word_ids)]
        print(self.chosen_words)
        self.started = True
        self.queue = self.chosen_words[['ka', 'hg', 'en']].sample(self.chosen_words.shape[0])
        self.startGame()

    def startGame(self):
        self.queue = self.chosen_words[['ka', 'hg', 'en']].sample(self.chosen_words.shape[0])
        self.current = 0
        self.displayQuestion(self.current)

    def textInputted(self, text):
        if len(self.prev_input_text) > len(text): # backspace was pressed
            
            self.input_text = self.input_text[:len(self.input_text)-1]
        else:
            if len(self.answer_input.text()) > 0:
                self.input_text += self.answer_input.text()[-1]

        self.prev_input_text = text
        # print(text)
        print(self.input_text)
        hiragana = self.convert.romajiToJapanese(self.input_text)
        print(hiragana)
        self.answer_input.setText(hiragana)


    def displayQuestion(self, idx):
        self.kanji_label.setText(self.queue['ka'].iloc[idx])
        self.setFontSize(self.kanji_label, self.kanji_fontsize)
        if self.display_en:
            self.english_label.setText(self.queue['en'].iloc[idx])
            self.setFontSize(self.english_label, self.english_fontsize)

    def checkAnswer(self, ans):
        return self.convert.romajiToJapanese(self.input_text) == ans

    def enterBtnPressed(self):
        self.prev_input_text = ""
        if self.started:
            is_correct = self.checkAnswer(self.queue['hg'].iloc[self.current])
            if is_correct:
                print("Correct!")
                # self.answer_label.setText("Correct!")
                self.answer_input.setStyleSheet("""
                    min-height: 50px;
                    min-width: 150px;
                    background-color: #02ce79;
                    font-family: 'Arial', sans-serif;
                    color: white;
                """)
            else:
                print("Incorrect!")
                # self.answer_label.setText("Not quite!")
                self.answer_input.setStyleSheet("""
                    min-height: 50px;
                    min-width: 150px;
                    background-color: #e74545;
                    font-family: 'Arial', sans-serif;
                    color: white;
                """)

            self.setFontSize(self.answer_label, self.answer_fontsize)
            # self.answer_label.setText("")
            self.timer = QtCore.QTimer(self)
            self.timer.setInterval(500)
            self.timer.timeout.connect(self.resetAnswerLabel)
            self.timer.start()
            self.answer_input.setText(None)
            self.input_text = ""
            self.current += 1
            if self.current < self.queue.shape[0]: # if there are still questions left
                self.displayQuestion(self.current)
            else:
                if self.loop_radio.isChecked(): # loop mode
                    self.startGame()
                elif self.timer_radio.isChecked():
                    print("Stop timer!")

    def resetAnswerLabel(self):
        # self.answer_label.setText("")
        self.answer_input.setStyleSheet("""
            min-height: 50px;
            min-width: 150px;
            font-family: 'Arial', sans-serif;
        """)

    def englishToggled(self, state):
        if state == 0:
            self.display_en = False
        else:
            self.display_en = True

    def setSelected(self, idx, state):
        self.words.loc[self.words['id'] == idx, 'selected'] = state

    # def textChanged(self, text):
    #     # width = self.answer_input.fontMetrics().width(text)
    #     # self.answer_input.setMinimumWidth(width)
    #     pass
    
    def timerRadioToggled(self, state):
        # if state:
        self.spin_box.setEnabled(state)

    def setFontSize(self, obj: QWidget, size: int):
        font = obj.font()
        font.setPointSize(size)
        obj.setFont(font)
        return obj

class KanjiSpellPage(QWidget):
    def __init__(self, level):
        super().__init__()
        self.level = level
        self.user = 1
        self.db = Database()
        self.colors = Color()

        self.words = self.db.get_words_at_level_user(self.level, self.user)
        # Flatten rows where word has multiple types by combining types into list
        combined_types = [[self.words['type'].iloc[i] for i in x] for x in self.words.groupby('word_id').groups.values()]
        combined_type_ids = [[self.words['type_id'].iloc[i] for i in x] for x in self.words.groupby('word_id').groups.values()]
        self.words = self.words.drop([j for sub in [y[1:] for y in [x for x in self.words.groupby('word_id').groups.values()]] for j in sub])
        self.words['type_id'] = combined_type_ids
        self.words['type'] = combined_types
        self.words.columns = ['id', 'ka', 'hg', 'en', 'level_id', 'type_id', 'type']

        # self.select_word_field = SelectWordField()

        self.container = QVBoxLayout()

        self.title_bar_layout = QHBoxLayout()
        self.title_bar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title = tools.getPageTitle(self.level)
        self.title_bar_layout.addWidget(self.title)

        self.container.addLayout(self.title_bar_layout)

        self.play_area = PlayArea(self.words)
        self.container.addWidget(self.play_area)

        self.setLayout(self.container)


