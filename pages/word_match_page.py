from database import Database
from bs4 import BeautifulSoup
import requests
import shutil
import random

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

styles = "assets\styles\styles.css"

class QCustomListWidget(QWidget):
    def __init__ (self, idx, jp, en, selected, parent = None):
        super(QCustomListWidget, self).__init__(parent)
        self.idx = idx
        self.text_vbox = QVBoxLayout()
        self.selected = selected

        self.jp_text = QLabel(f'{jp}')
        self.en_text = QLabel(en)

        self.text_vbox.addWidget(self.jp_text)
        self.text_vbox.addWidget(self.en_text)
        self.text_vbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # self.clicked.connect(self.itemClicked)

        self.selected_style = 'color: rgb(3, 133, 3);'
        self.unselected_style = 'color: rgb(0, 0, 0);'

        self.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

        self.setLayout(self.text_vbox)

    def clicked(self):
        if self.selected: # If item is selected when it is pressed, it should now be displayed as unselected
            self.jp_text.setStyleSheet(self.unselected_style)
            self.en_text.setStyleSheet(self.unselected_style)
        else:
            self.jp_text.setStyleSheet(self.selected_style)
            self.en_text.setStyleSheet(self.selected_style)
        
        self.selected = not self.selected

    def getSelected(self):
        return self.selected

    def getIdx(self):
        return self.idx

class SelectWordField(QWidget):
    def __init__(self, parent=None, words=None):
        super().__init__(parent)
        self.words = words

        self.outer_container = QVBoxLayout()

        self.title = QLabel('Word List')
        font = self.title.font()
        font.setPointSize(20)
        self.title.setFont(font)

        self.outer_container.addWidget(self.title)

        self.random_btn = QPushButton('Randomise')
        self.random_btn.setMaximumWidth(100)
        self.random_btn.setProperty("class", "button")
        self.random_btn.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.random_btn.clicked.connect(self.randomBtnPressed)

        self.outer_container.addWidget(self.random_btn)

        self.list_widget = QListWidget()
        self.list_items = [QCustomListWidget(idx=words['id'].iloc[i], jp=words['ka'].iloc[i], en=words['en'].iloc[i], selected=False) for i in range(self.words.shape[0])]
        for item in self.list_items:
            my_list_widget = QListWidgetItem(self.list_widget)
            # Set size hint
            my_list_widget.setSizeHint(item.sizeHint())
            # Add QListWidgetItem into QListWidget
            self.list_widget.addItem(my_list_widget)
            self.list_widget.setItemWidget(my_list_widget, item)

        self.list_widget.itemClicked.connect(self.updateItem)

        self.outer_container.addWidget(self.list_widget)
        self.outer_container.setProperty("class", "select")

        with open(styles, "r") as f:
            self.setStyleSheet(f.read())

        self.setLayout(self.outer_container)

    def getChosenWords(self):
        return [word.getIdx() for word in self.list_items if word.getSelected()]

    def updateItem(self):
        print(f'{self.list_widget.currentRow()} clicked!')
        self.list_items[self.list_widget.currentRow()].clicked()
        self.parent().setSelected(self.list_items[self.list_widget.currentRow()].getIdx(), self.list_items[self.list_widget.currentRow()].getSelected())

    def randomBtnPressed(self):
        self.parent().randomBtnPressed()

    def rowChanged(self, idx):
        self.parent().grammarSelected(idx)

    def scrollListView(self, idx):
        self.list_widget.scrollToItem(self.list_widget.item(idx))

class ScoreTracker:
    def __init__(self, c=0, t=0):
        self.correct = c
        self.total = t
        self.round_words_remaining = None

    def getTotal(self):
        return self.total
    
    def getCorrect(self):
        return self.correct
    
    def answerCorrect(self):
        self.correct += 1

    def setTotal(self, t):
        self.total = t

    def setWordsRemaining(self, n):
        self.round_words_remaining = n

    def decrementRemaining(self):
        if self.round_words_remaining > 0:
            self.round_words_remaining -= 1
        return self.round_words_remaining

class PlayArea(QWidget):
    def __init__(self, n, words, show_hg):
        super().__init__()
        self.size = n
        self.words = words
        self.show_hg = show_hg
        self.num_words = 8
        self.pressed_button = {'id': None, 'type': None} # store info of button pressed first to compare to info of second pressed button to check for a match
        self.container = QHBoxLayout()
        self.button_container = QGridLayout()
        self.select_words_container = QVBoxLayout()
        self.started = False

        print("Words:")
        print(self.words)

        self.score_tracker = ScoreTracker(c=0, t=0)
        self.score_label = QLabel(f'{self.score_tracker.getCorrect()} / {self.score_tracker.getTotal()}')
        font = self.score_label.font()
        font.setPointSize(24)
        self.score_label.setFont(font)

        self.score_title = QLabel('Score:')
        font = self.score_title.font()
        font.setPointSize(24)
        self.score_title.setFont(font)

        self.score_container = QHBoxLayout()
        self.score_container.addWidget(self.score_title)
        self.score_container.addWidget(self.score_label)

        self.select_words_field = SelectWordField(parent=self, words=self.words)

        self.start_button = QPushButton()
        self.start_button.setMinimumHeight(50)
        self.start_button.clicked.connect(self.startBtnPressed)
        self.start_button_layout = QHBoxLayout()
        self.start_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.start_label = QLabel('Start')
        self.start_button_layout.addWidget(self.start_label)
        self.start_button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.start_button.setLayout(self.start_button_layout)

        self.select_words_container.addLayout(self.score_container)
        self.select_words_container.addWidget(self.select_words_field)
        self.select_words_container.addWidget(self.start_button)
        self.container.addLayout(self.button_container)
        self.container.addLayout(self.select_words_container)

        # Initialise play area buttons with blank text
        self.buttons = {'jp': [WordButton(id=i) for i in range(self.num_words)], 'en': [WordButton(id=i) for i in range(self.num_words)]}
        
        self.populateArea()
        self.setLayout(self.container)

    def startBtnPressed(self):
        self.started = True
        self.resetBtnText()
        chosen_words = self.words[self.words['selected'] == True]
        self.num_words = min((self.size**2)//2, chosen_words.shape[0])
        print(f'num words: {self.num_words}')
        print("Chosen words:")
        print(chosen_words)
        jp_words, en_words = self.pickWords(chosen_words)
        for i in range(self.num_words):
            self.buttons['jp'][i].setJp(ka=jp_words['ka'].iloc[i], hg=jp_words['hg'].iloc[i])
            print("Japanese word:")
            print(jp_words['ka'].iloc[i])
            self.buttons['en'][i].setEn(en=en_words['en'].iloc[i])
            print("English word")
            print(en_words['en'].iloc[i])
        
    def btnPressed(self, type, id):
        print(self.pressed_button)
        if self.pressed_button['type'] is None: # this is the first button pressed of a new pair
            self.pressed_button['id'] = id
            self.pressed_button['type'] = type
            if not type is None: # if selecting a button with text
                self.buttons[type][id].setSelectedStyle()
        else:
            if id == self.pressed_button['id'] and type != self.pressed_button['type']:
                print("match!")
                self.buttons[type][id].resetBtn()
                self.buttons[self.pressed_button['type']][self.pressed_button['id']].resetBtn()
            else:
                print("no match!")
            # if not type is None: # if selecting a button with text
            self.buttons[self.pressed_button['type']][self.pressed_button['id']].setUnselectedStyle()
            self.pressed_button['id'] = None
            self.pressed_button['type'] = None

        print(self.pressed_button)

    def toggleHg(self):
        self.show_hg = not self.show_hg
        for i in range(len(self.buttons['jp'])):
            self.buttons['jp'][i].toggleHg()
            
    def setSelected(self, idx, state):
        self.words.loc[self.words['id'] == idx, 'selected'] = state

    def resetBtnText(self):
        # Set text of all buttons to blank
        for i in range(len(self.buttons['jp'])):
            self.buttons['jp'][i].resetBtn()
        for i in range(len(self.buttons['en'])):
            self.buttons['en'][i].resetBtn()

    def setWords(self, words):
        self.resetBtnText()
        self.words = words
        self.num_words = min((self.size**2)//2, (self.words.shape[0]-(self.words.shape[0]%2)))
        print("Num words:")
        print(self.num_words)

    def pickWords(self, words):
        # Pick the words to use in the matching. If number of available words is less than grid size requires, pick greatest even number less than size.
        sample = words.sample(self.num_words)
        jp_words = sample[['ka', 'hg']]
        en_words = sample[['en']]
        return jp_words, en_words
    
    def populateArea(self):
        nums = list(range(0, self.num_words*2)) # account for japanese and english counterparts
        random.shuffle(nums)
        print("Numbers chosen for this round:")
        print(nums)
        for i in range(0, self.num_words):
            # populate with the japanese words
            self.button_container.addWidget(self.buttons['jp'][i], nums[2*i]//self.size, nums[2*i]%self.size)
            print(f'x: {nums[2*i]//self.size}, y: {nums[2*i]%self.size}')

            # populate with the english words
            self.button_container.addWidget(self.buttons['en'][i], nums[2*i+1]//self.size, nums[2*i+1]%self.size)
            print(f'x: {nums[2*i+1]//self.size}, y: {nums[2*i+1]%self.size}')

class WordButton(QWidget):
    def __init__(self, id, show_hg=True, ka=None, hg=None, en=None, type=None):
        super().__init__()
        self.show_hg = show_hg
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
                background-color: #ebebe7;
            }
                                  
            # QPushButton:pressed {
            #     background-color: #94d7f7;                      
            # }"""
        self.button.setStyleSheet(self.unselected_style)
        
        with open(styles, "r") as f:
            self.setStyleSheet(f.read())

        self.button.setLayout(self.button_layout)
        self.button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.button.clicked.connect(self.pressed)

        self.container = QHBoxLayout()
        self.container.addWidget(self.button)
        self.setLayout(self.container)
    
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
            self.setJp(self.ka, self.hg)

    def setEn(self, en):
        self.type = 'en'
        self.button_text = f"{en}"
        self.setBtnText()

    def resetBtn(self):
        self.button_text = ""
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
        self.words['selected'] = [False for i in range(self.words.shape[0])]

        # print(self.words)

        self.title_bar_layout = QHBoxLayout()
        self.title_bar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.title_bar_layout.setSpacing(200)

        self.meta_buttons_container = QHBoxLayout()
        self.meta_buttons_container.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.reset_button = QPushButton('Reset')
        self.reset_button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.reset_button.setMinimumWidth(150)
        self.reset_button.setMaximumHeight(40)

        font = self.reset_button.font()
        font.setPointSize(18)
        self.reset_button.setFont(font)

        self.toggle_hg_button = QPushButton('Hide hiragana')
        self.toggle_hg_button.clicked.connect(self.toggleHg)
        self.toggle_hg_button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.toggle_hg_button.setMinimumWidth(150)
        self.toggle_hg_button.setMaximumHeight(40)
        font = self.toggle_hg_button.font()
        font.setPointSize(14)
        self.toggle_hg_button.setFont(font)

        self.meta_buttons_container.addWidget(self.reset_button)
        self.meta_buttons_container.addWidget(self.toggle_hg_button)

        self.title_bar_layout.addLayout(self.meta_buttons_container)   

        self.title = QLabel(f'{level.upper()} Word Match')
        font = self.title.font()
        font.setPointSize(24)
        self.title.setFont(font)
        self.title.setStyleSheet(f"""
        color: #{self.colors.get_level_color(self.level)};
        font-family: Titillium;
        """)
       
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

        self.setLayout(self.outer_container)

    def toggleHg(self):
        self.show_hg = not self.show_hg
        if self.show_hg:
            self.toggle_hg_button.setText('Hide hiragana')
        else:
            self.toggle_hg_button.setText('Show hiragana')
        self.play_area.toggleHg()