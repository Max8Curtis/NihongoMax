from database import Database
from bs4 import BeautifulSoup
import requests
import shutil
import random
from romaji.convert import Convert
import time
import pykakasi

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

class MyQLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()

    keyPressed = QtCore.pyqtSignal(int)

    def keyPressEvent(self, event):
        super(QLineEdit, self).keyPressEvent(event)
        self.keyPressed.emit(event.key())

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
        self.english_fontsize = 20
        self.answer_fontsize = 32
        self.timer_fontsize = 16
        self.current_text_hg = ""
        self.convert = Convert()
        self.kks = pykakasi.kakasi()
        self.time_limit = 1

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

        self.kanji_label = QLabel('--')
        self.setFontSize(self.kanji_label, self.kanji_fontsize)
        self.kanji_label.setToolTip(None)

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
        # self.answer_input.keyPressed.connect(self.onKey)
        self.setFontSize(self.answer_input, 14)

        self.enter_button = QPushButton()
        self.enter_button.setMinimumHeight(60)
        self.enter_button.setMinimumWidth(80)
        self.enter_button_layout = QHBoxLayout()
        self.enter_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.enter_label = QLabel('Enter')
        self.setFontSize(self.enter_label, 14)
        self.enter_button_layout.addWidget(self.enter_label)
        self.enter_button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.enter_button.setProperty("class", "button")
        self.enter_button.setLayout(self.enter_button_layout)
        self.enter_button.clicked.connect(self.enterBtnPressed)

        self.timer_label = QLabel(None)
        self.setFontSize(self.timer_label, self.timer_fontsize)
        
        self.play_area_container.addWidget(self.timer_label, 0, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.play_area_container.addWidget(self.kanji_label, 1, 1, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.play_area_container.addWidget(self.english_label, 2, 1, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.play_area_container.addWidget(self.answer_label, 3, 1, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.play_area_container.addWidget(self.answer_input, 5, 1, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.play_area_container.addWidget(self.enter_button, 5, 3, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        self.play_area_container.setColumnStretch(0,1)
        self.play_area_container.setColumnStretch(4,1)
        self.play_area_container.setRowStretch(4,1)
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
        if self.chosen_words.shape[0] > 0:
            self.started = True
            self.queue = self.chosen_words[['ka', 'hg', 'en']].sample(self.chosen_words.shape[0])
            self.startGame()
        else:
            self.started = False
            self.english_label.setText("Please select some words")
            self.timer = QtCore.QTimer(self)
            self.timer.setInterval(2000)
            self.timer.timeout.connect(self.resetEnglishLabel)
            self.timer.start()

    def resetEnglishLabel(self):
        self.english_label.setText(None)
        self.setFontSize(self.english_label, self.english_fontsize)

    def startGame(self):
        self.queue = self.chosen_words[['ka', 'hg', 'en']].sample(self.chosen_words.shape[0])
        self.current = 0
        if self.timer_radio.isChecked():
            self.time_limit = self.spin_box.value()
            print(self.time_limit)
            self.countdown()
            
        self.displayQuestion()

    def countdown(self):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateTimer)
        self.timer.start(1000)
        self.updateTimerLabel()

    def updateTimer(self):
        self.time_limit -= 1
        self.updateTimerLabel()
        if self.time_limit == 0:
            self.started = False
            self.timer.stop()
            self.resetGame()
            return None
        
        print(f"Time left: {self.time_limit}")
        
    def resetGame(self):
        self.time_limit = 0
        self.resetEnglishLabel()
        self.resetAnswerLabel()
        self.resetAnswerInput()
        self.resetTimerLabel()
        self.resetKanjiLabel()
        self.started = False

    def updateTimerLabel(self):
        mins = self.time_limit // 60
        secs = self.time_limit % 60
        if mins == 0 and secs <= 5:
            self.timer_label.setStyleSheet("""
                color: red;                  
            """)
        else:
            self.timer_label.setStyleSheet("""
                color: black;                  
            """)
        self.timer_label.setText(f"{'{:02d}'.format(mins)}:{'{:02d}'.format(secs)}")

    def onKey(self, key):
        # Test for back space key pressed
        if key == 16777219:
            print('back key pressed')
            if len(self.current_input_text) > 0:
                self.current_input_text_hg = self.current_input_text_hg[:len(self.current_input_text_hg)-1]
                self.textInputted(self.answer_input.text())
        elif len(self.answer_input.text()) != len(self.previous_input_text_hg):
            self.textInputted(self.answer_input.text())

    def textInputted(self, text):
        # print(f"Current: {text}")
        text = text.replace(" ", "").replace("'", '’')
        current_input_text = self.convert.romajiToJapanese(text)
        self.current_text_hg = current_input_text
        self.answer_label.setText(current_input_text)
        self.setFontSize(self.answer_label, self.answer_fontsize)

    def displayQuestion(self):
        self.kanji_label.setText(self.queue['ka'].iloc[self.current])
        self.setFontSize(self.kanji_label, self.kanji_fontsize)
        self.kanji_label.setToolTip(self.queue['hg'].iloc[self.current])
        self.displayEnglish()

    def checkAnswer(self, ans):
        # return self.convert.romajiToJapanese(self.input_text) == ans
        print(f"Input: {self.current_text_hg}, answer: {ans}")
        return self.current_text_hg == ans

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
                self.answer_label

            self.setFontSize(self.answer_label, self.answer_fontsize)
            self.answer_timer = QtCore.QTimer(self)
            # self.answer_timer.setInterval(750)
            self.answer_timer.timeout.connect(self.resetAnswerLabel)
            self.answer_timer.start(750)
            self.answer_input.setText(None)
            self.current_text_hg = ""
            self.answer_label.setText(None)
            self.current += 1
            if self.current < self.queue.shape[0]: # if there are still questions left
                self.displayQuestion()
            else:
                if self.loop_radio.isChecked(): # loop mode
                    self.startGame()
                elif self.timer_radio.isChecked():
                    self.timer.stop()
                    self.resetGame()

    def resetKanjiLabel(self):
        self.kanji_label.setText("--")

    def resetTimerLabel(self):
        self.timer_label.setText(None)

    def resetAnswerInput(self):
        self.answer_input.setText(None)

    def resetTimerLabel(self):
        self.timer_label.setText(None)

    def resetAnswerLabel(self):
        # self.answer_label.setText("")
        self.answer_input.setStyleSheet("""
            min-height: 50px;
            min-width: 150px;
            font-family: 'Arial', sans-serif;
        """)

    def displayEnglish(self):
        if self.started:
            if self.display_en:
                self.english_label.setText(self.queue['en'].iloc[self.current])
                self.setFontSize(self.english_label, self.english_fontsize)
            else:
                self.english_label.setText(None)

    def englishToggled(self, state):
        if state == 0:
            self.display_en = False
        else:
            self.display_en = True

        self.displayEnglish()
            
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


