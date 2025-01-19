from database import Database
from bs4 import BeautifulSoup
import requests
import shutil
import random
import numpy as np

import math

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, 
    QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QToolBar,
    QStatusBar, QStackedLayout, QGridLayout, QCheckBox, QMenu,
    QDialog, QDialogButtonBox, QComboBox, QListWidget, QListWidgetItem
)
from PyQt6.QtGui import QPixmap, QAction, QCursor
from PyQt6 import QtCore
from assets.styles.colors import Color
from assets.widgets import SelectWordField, StartButton
from assets.tools import Tools
tools = Tools()

styles = "assets\styles\styles.css"

class ScoreTracker(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.round_words_remaining = None
        self.points_correct = 5
        self.points_incorrect = -3
        self.score = 0
    
    def getScore(self):
        return self.score
    
    def answerCorrect(self):
        self.score += self.points_correct
        self.parent().updateScoreLabel()
        # self.decrementRemaining()

    def answerIncorrect(self):
        self.score += self.points_incorrect
        self.parent().updateScoreLabel()

    def setWordsRemaining(self, n):
        self.round_words_remaining = n

    def decrementRemaining(self):
        if self.round_words_remaining is None:
            return None
        if self.round_words_remaining > 0:
            self.round_words_remaining -= 1
        return self.round_words_remaining
    
    def resetScore(self):
        self.round_words_remaining = None
        self.score = 0

class PlayArea(QWidget):
    def __init__(self, n, words, show_hg):
        super().__init__()
        self.size = n
        self.words = words
        self.show_hg = show_hg
        self.num_words = 8
        self.pressed_button = {'idx': None, 'type': None} # store info of button pressed first to compare to info of second pressed button to check for a match
        self.container = QHBoxLayout()
        self.container.setContentsMargins(0,0,0,0)
        self.button_container = QGridLayout()
        self.select_words_container = QVBoxLayout()
        self.select_words_container.setContentsMargins(0,0,0,0)
        self.started = False

        self.words['selected'] = [False for i in range(self.words.shape[0])]

        print("Words:")
        print(self.words)

        self.score_tracker = ScoreTracker(parent=self)
        self.score_label = QLabel(f'{self.score_tracker.getScore()}')
        self.score_label.setObjectName("scoreLabel")
        # self.setFontSize(self.score_label, 24)

        self.score_title = QLabel('Score:')
        self.score_title.setObjectName("scoreTitle")
        # self.setFontSize(self.score_title, 24)

        self.score_container = QHBoxLayout()
        self.score_container.setContentsMargins(10,0,0,0)
        self.score_container.addWidget(self.score_title)
        self.score_container.addWidget(self.score_label)

        self.select_words_field = SelectWordField(parent=self, words=self.words)

        # self.start_button = QPushButton()
        # self.start_button.setMinimumHeight(50)
        # self.start_button.clicked.connect(self.startBtnPressed)
        # self.start_button_layout = QHBoxLayout()
        # self.start_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.start_label = QLabel('Start')
        # self.setFontSize(self.start_label, 18)
        # self.start_button_layout.addWidget(self.start_label)
        # self.start_button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        # self.start_button.setProperty("class", "button")
        # self.start_button.setLayout(self.start_button_layout)
        self.start_button = StartButton()
        # self.start_button.clicked.connect(self.startBtnPressed)

        self.select_words_container.addLayout(self.score_container)
        self.select_words_container.addWidget(self.select_words_field)
        self.select_words_container.addWidget(self.start_button)
        self.container.addLayout(self.button_container)
        self.container.addLayout(self.select_words_container)

        # Initialise play area buttons with blank text
        self.buttons = [WordButton() for i in range(self.size**2)]
        for i in range(len(self.buttons)):
            self.button_container.addWidget(self.buttons[i], i//self.size, i%self.size)
        
        # self.populateArea()

        # with open(styles, "r") as f:
        #     self.setStyleSheet(f.read())

        # print(self.button_container.itemAtPosition(0,0))
        self.setLayout(self.container)

    def startBtnPressed(self):
        self.score_tracker.resetScore()
        self.updateScoreLabel()
        self.words.assign(selected=False)
        self.started = True
        self.resetButtons()
        # self.chosen_words = self.words[self.words['selected'] == True]
        chosen_word_ids = self.select_words_field.getChosenWords()
        self.chosen_words = self.words[self.words['id'].isin(chosen_word_ids)]
        self.num_words = min((self.size**2)//2, self.chosen_words.shape[0])
        print(f'num words: {self.num_words}')
        self.startRound()

    def startRound(self):
        sampled_words = self.pickWords(self.chosen_words)
        print(sampled_words)
        nums = list(range(0, self.num_words*2)) # account for japanese and english counterparts
        random.shuffle(nums)
        print("Numbers chosen for this round:")
        print(nums)
        self.score_tracker.setWordsRemaining(self.num_words)
        for i in range(0, self.num_words):
            self.buttons[nums[2*i]].setData(id=sampled_words['id'].iloc[i], type='jp', ka=sampled_words['ka'].iloc[i], hg=sampled_words['hg'].iloc[i])
            print(f"Japanese word: {sampled_words['ka'].iloc[i]} going to button {nums[i]}")
            print()
            self.buttons[nums[2*i+1]].setData(id=sampled_words['id'].iloc[i], type='en', en=sampled_words['en'].iloc[i])
            print(f"English word: {sampled_words['en'].iloc[i]} going to button {nums[i+1]}")
            print()

            self.buttons[nums[2*i]].displayText()
            self.buttons[nums[2*i+1]].displayText()

    def getButtonIndex(self, id, type):
        # Get list index of button with word id <id> from the buttons list
        for i in range(len(self.buttons)):
            if self.buttons[i].getId() == id and self.buttons[i].getType() == type:
                return i
        return None # no button in the list contains a word with that <id>

    def btnPressed(self, type, id):
        print(self.pressed_button)
        idx = self.getButtonIndex(id, type)
        print(f"Button index: {idx}")
        if self.pressed_button['type'] is None: # this is the first button pressed of a new pair
            self.pressed_button['idx'] = idx
            self.pressed_button['type'] = type
            if not type is None: # if selecting a button with text
                self.buttons[idx].setSelectedStyle()
        else: # this is the second button pressed
            # check if the first and second pressed buttons have the same word id and opposing types (i.e. they match)
            if id == self.buttons[self.pressed_button['idx']].getId() and type != self.pressed_button['type']:
                print("match!")
                self.buttons[idx].resetBtn()
                self.buttons[self.pressed_button['idx']].resetBtn()
                self.score_tracker.answerCorrect()
                remaining = self.score_tracker.decrementRemaining()
                print(remaining)
                if remaining == 0:
                    self.startRound()
            elif type is None: # the second button pressed is blank
                pass
            else:
                print("no match!")
                self.score_tracker.answerIncorrect()
            # if not type is None: # if selecting a button with text
            self.buttons[self.pressed_button['idx']].setUnselectedStyle()
            self.pressed_button['idx'] = None
            self.pressed_button['type'] = None

        print(self.pressed_button)

    def updateScoreLabel(self):
        self.score_label.setText(f'{self.score_tracker.getScore()}')
        self.setFontSize(self.score_label, 24)

    def toggleHg(self):
        self.show_hg = not self.show_hg
        for i in range(len(self.buttons)):
            self.buttons[i].toggleHg()
            
    def setSelected(self, idx, state):
        self.words.loc[self.words['id'] == idx, 'selected'] = state

    def resetButtons(self):
        # Set text of all buttons to blank
        for i in range(len(self.buttons)):
            self.buttons[i].resetBtn()

    def setWords(self, words):
        self.resetBtnText()
        self.words = words
        self.num_words = min((self.size**2)//2, (self.words.shape[0]-(self.words.shape[0]%2)))
        print("Num words:")
        print(self.num_words)

    def pickWords(self, words):
        # Pick the words to use in the matching. If number of available words is less than grid size requires, pick greatest even number less than size.
        sample = words.sample(self.num_words)
        return sample

    def setFontSize(self, obj: QWidget, size: int):
        font = obj.font()
        font.setPointSize(size)
        obj.setFont(font)
        return obj
    
    def keyPressEvent(self, event):
        # Override the key pressing event to handle ESCAPE, where currently selected button should be deselected
        if event.key() == Qt.Key.Key_Escape:
            if not self.pressed_button['idx'] is None:
                self.buttons[self.pressed_button['idx']].setUnselectedStyle()
                for x in list(self.pressed_button.keys()):
                    self.pressed_button[x] = None
            # self.key_label.setText('Key Event: Escape Pressed')

    
class WordButton(QWidget):
    def __init__(self, id=None, type=None, ka=None, hg=None, en=None):
        super().__init__()
        self.show_hg = True
        self.type = type
        self.id = id
        self.ka = ka
        self.hg = hg
        self.en = en

        self.button_layout = QVBoxLayout()
        self.button_layout.setSpacing(-10)
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.button_text = ""
        self.button_label = QLabel(self.button_text)
        self.button_label.setWordWrap(True)
        self.button_layout.addWidget(self.button_label)

        self.button = QPushButton()
        self.unselected_style = """
            QPushButton {
                border-radius: 5px;
                background-color: #cccccc;
                min-width: 180px;
                min-height: 120px;
                font-size: 20px;
                font-family: Verdana;
            }

            QPushButton:hover {
                background-color: #ebebe7;
            }
                                  
            # QPushButton:pressed {
            #     background-color: #94d7f7;                      
            # }
        """
        self.selected_style = """
            QPushButton {
                border-radius: 5px;
                background-color: #9ccbf5;
                min-width: 180px;
                min-height: 120px;
                font-size: 20px;
                font-family: Verdana;
            }

            QPushButton:hover {
                background-color: #b7e3f7;
            }
                                  
            # QPushButton:pressed {
            #     background-color: #94d7f7;                      
            # }"""
        self.button.setStyleSheet(self.unselected_style)
        
        # with open(styles, "r") as f:
        #     self.setStyleSheet(f.read())

        self.button.setLayout(self.button_layout)
        self.button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.button.clicked.connect(self.pressed)

        self.container = QHBoxLayout()
        self.container.addWidget(self.button)
        self.setLayout(self.container)

    def setData(self, id, type, ka=None, hg=None, en=None):
        self.id = id
        self.type = type
        self.ka = ka
        self.hg = hg
        self.en = en

    def displayText(self):
        if self.type is None:
            self.button_text = ""
        else:
            if self.type == 'en':
                self.button_text = self.en
            elif self.type == 'jp':
                if self.show_hg:
                    self.button_text = f"{self.ka} \n {self.hg}"
                else:
                    self.button_text = self.ka 
        self.setBtnText()
    
    def setSelectedStyle(self):
        self.button.setStyleSheet(self.selected_style)

    def setUnselectedStyle(self):
        self.button.setStyleSheet(self.unselected_style)

    def setJp(self, ka, hg):
        self.ka = ka
        self.hg = hg
        self.type = 'jp'
        if self.show_hg:
            self.button_text = f"{self.ka} \n {self.hg}"
        else:
            self.button_text = self.ka
        self.setBtnText()

    def toggleHg(self):
        self.show_hg = not self.show_hg
        if not self.type is None:
            self.displayText()

    def setEn(self, en):
        self.type = 'en'
        self.button_text = f"{en}"
        self.setBtnText()

    def resetBtn(self):
        self.button_text = ""
        self.ka = None
        self.hg = None
        self.en = None
        self.type = None
        self.setBtnText()

    def setBtnText(self):
        self.button_label.setText(self.button_text)
        font = self.button_label.font()
        if self.type == 'jp':
            font.setPointSize(18)
        else:
            font.setPointSize(12)
        self.button_label.setFont(font)

    def getId(self):
        return self.id
    
    def getType(self):
        return self.type

    def pressed(self):
        self.parent().btnPressed(self.type, self.id)



class WordMatchPage(QWidget):
    def __init__(self, level):
        super().__init__()
        self.level = level
        self.user = 1 # user is static for now
        self.show_hg = True
        self.colors = Color()

        self.db = Database()

        self.words = self.db.get_words_at_level_user(self.level, self.user)
        # Flatten rows where word has multiple types by combining types into list
        combined_types = [[self.words['type'].iloc[i] for i in x] for x in self.words.groupby('word_id').groups.values()]
        combined_type_ids = [[self.words['type_id'].iloc[i] for i in x] for x in self.words.groupby('word_id').groups.values()]
        self.words = self.words.drop([j for sub in [y[1:] for y in [x for x in self.words.groupby('word_id').groups.values()]] for j in sub])
        self.words['type_id'] = combined_type_ids
        self.words['type'] = combined_types
        self.words.columns = ['id', 'ka', 'hg', 'en', 'level_id', 'type_id', 'type']

        self.title_bar_layout = QHBoxLayout()
        self.title_bar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.meta_buttons_container = QHBoxLayout()
        self.meta_buttons_container.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.toggle_hg_button = QPushButton('Hide hiragana')
        self.toggle_hg_button.clicked.connect(self.toggleHg)
        self.toggle_hg_button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        # self.toggle_hg_button.setMinimumWidth(150)
        # self.toggle_hg_button.setMaximumHeight(40)
        self.toggle_hg_button.setObjectName("toggleHiraganaButton")
        # self.setFontSize(self.toggle_hg_button, 14)

        self.meta_buttons_container.addWidget(self.toggle_hg_button)

        self.title_bar_layout.addLayout(self.meta_buttons_container)   

        # self.title = QLabel(f'{level.upper()} Word Match')
        # self.setFontSize(self.title, 24)
        # self.title.setStyleSheet(tools.getPageTitleStyling(self.level))
        self.title = tools.getPageTitle(self.level, "Word Match")
        self.title.setObjectName("pageTitle"+level)
       
        self.title_bar_layout.addStretch(1)
        self.title_bar_layout.addWidget(self.title)
        self.title_bar_layout.addStretch(1)
        self.title_bar_layout.addStretch(1)

        self.inner_hbox = QHBoxLayout()

        self.play_area = PlayArea(4, self.words, self.show_hg)

        # self.select_word_field = SelectWordField(self.level, self.user, self, self.db, self.words)

        self.inner_hbox.addWidget(self.play_area)
        # self.inner_hbox.addWidget(self.select_word_field)

        self.outer_container = QVBoxLayout()
        self.outer_container.addLayout(self.title_bar_layout)
        self.outer_container.addLayout(self.inner_hbox)

        # self.select_button = QPushButton('Select Words')
        # self.select_button.clicked.connect(self.selectWords)
        # self.outer_container.addWidget(self.select_button)

        # with open(styles, "r") as f:
        #     self.setStyleSheet(f.read())

        self.setLayout(self.outer_container)

    def toggleHg(self):
        self.show_hg = not self.show_hg
        if self.show_hg:
            self.toggle_hg_button.setText('Hide hiragana')
        else:
            self.toggle_hg_button.setText('Show hiragana')
        self.play_area.toggleHg()

    def setFontSize(self, obj: QWidget, size: int):
        font = obj.font()
        font.setPointSize(size)
        obj.setFont(font)
        return obj