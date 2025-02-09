from database import Database
from bs4 import BeautifulSoup
import requests
import shutil
import random
from romaji.convert import Convert
import time
import pykakasi
import itertools
import pandas as pd

from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel,
    QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QToolBar,
    QStatusBar, QStackedLayout, QGridLayout, QCheckBox, QMenu,
    QDialog, QDialogButtonBox, QComboBox, QScrollArea, QListWidget,
    QAbstractButton, QListWidgetItem, QRadioButton, QSpinBox, QToolTip,
    QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QAction, QCursor, QPainter, QBrush
from PyQt6 import QtCore
from assets.styles.colors import Color
from assets.widgets import SelectWordField, StartButton, QCustomListWidget
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


class QCustomTextListWidget(QCustomListWidget):
    def __init__(self, idx, jp, en, selected, parent=None):
        super(QCustomListWidget, self).__init__(parent)

    def clicked(self):
        pass


class ResetButton(QWidget):
    def __init__(self):
        super().__init__()
        self.button = QPushButton()
        self.button.setObjectName("playButton")

        self.button_layout = QHBoxLayout()
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button_icon = QLabel(self)
        pixmap = QPixmap(r"assets/images/reset.jpg").scaled(15, 15)
        self.button_icon.setPixmap(pixmap)
        self.button_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button_layout.addWidget(self.button_icon)
        self.button.setLayout(self.button_layout)

        self.button.setCursor(
            QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.button.clicked.connect(self.buttonClicked)

        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

    def buttonClicked(self):
        pass


class PlayButton(QWidget):
    def __init__(self):
        super().__init__()
        self.started = False

        self.button = QPushButton()
        self.button.setObjectName("playButton")

        self.button_layout = QHBoxLayout()
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.button_icon = QLabel(self)
        pixmap = QPixmap(r"assets/images/play.png").scaled(15, 15)
        self.button_icon.setPixmap(pixmap)
        self.button_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button_layout.addWidget(self.button_icon)
        self.button.setLayout(self.button_layout)

        self.button.setCursor(
            QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.button.clicked.connect(self.buttonClicked)

        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

    def buttonClicked(self):
        self.started = not self.started
        if self.started:
            pixmap = QPixmap(r"assets/images/pause.png").scaled(15, 15)
            self.parent().startTimer()
        else:
            pixmap = QPixmap(r"assets/images/play.png").scaled(15, 15)
            self.parent().stopTimer()

        self.button_icon.setPixmap(pixmap)


class SelectTextField(QWidget):
    def __init__(self, db, user):
        super().__init__()
        self.db = db
        self.user = user

        self.types = self.db.get_text_types()
        # self.types = types
        self.texts = self.db.get_user_texts(user)
        print(self.texts)
        self.selected_type_idx = 0

        self.type_labels = self.getTypesCombinations()
        print(self.type_labels)

        self.outer_container = QVBoxLayout()

        self.widget_layout = QVBoxLayout()

        self.widget = QWidget()
        self.widget.setObjectName("selectTextWidget")

        self.title = QLabel('Text List')
        self.title.setObjectName("selectWordFieldTitle")

        self.widget_layout.addWidget(self.title)

        self.filter_buttons_layout = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("selectTextSearchBar")
        self.search_bar.textChanged.connect(self.textSearchUpdated)

        self.type_combobox = QComboBox()
        self.type_combobox.setObjectName("selectTextTypeComboBox")
        self.type_combobox.addItems(self.type_labels['label'])
        self.type_combobox.currentIndexChanged.connect(
            self.updateTypeSelection)

        self.random_btn = QPushButton('Randomise')
        # self.random_btn.setMaximumWidth(100)
        self.random_btn.setObjectName("randomiseButton")
        self.random_btn.setCursor(
            QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.random_btn.clicked.connect(self.randomBtnPressed)

        self.filter_buttons_layout.addWidget(self.search_bar)
        self.filter_buttons_layout.addWidget(self.type_combobox)
        self.filter_buttons_layout.addWidget(self.random_btn)

        self.widget_layout.addLayout(self.filter_buttons_layout)

        self.list_widget = QListWidget()
        self.list_items = []
        self.filterListItems()
        self.populateList()

        self.widget_layout.addWidget(self.list_widget)

        self.widget.setLayout(self.widget_layout)
        self.widget.setObjectName("selectTextField")
        self.outer_container.addWidget(self.widget)

        self.setLayout(self.outer_container)

        # self.outer_container.addWidget(self.random_btn)

    def textSearchUpdated(self, text):
        if text == "":
            self.filterListItems()
        else:
            self.filterListItems(text)
            print(text)

        self.populateList()

    def updateTypeSelection(self, index):
        self.selected_type_idx = index
        self.filterListItems()
        self.populateList(index)

    def filterListItems(self, filter_ex=None):
        # TODO:
        #  Add sophisticated searching and order list items by similarity to the search text
        ##
        if filter_ex is None:
            self.list_items = [QCustomListWidget(idx=self.texts['id'].iloc[i], jp=self.texts['title'].iloc[i], en=f"{self.texts['author'].iloc[i]} - Length: {self.texts['length'].iloc[i]} - PB: {self.texts['pb'].iloc[i] if not pd.isna(self.texts['pb'].iloc[i]) else '-'}", selected=False) for i in range(
                self.texts.shape[0]) if self.texts['type_id'].iloc[i] == self.type_labels['id'][self.selected_type_idx]]
        else:
            filter_ex = filter_ex.lower()
            self.list_items = [QCustomListWidget(idx=self.texts['id'].iloc[i], jp=self.texts['title'].iloc[i], en=f"{self.texts['author'].iloc[i]} - Length: {self.texts['length'].iloc[i]} - PB: {self.texts['pb'].iloc[i] if not pd.isna(self.texts['pb'].iloc[i]) else '-'}", selected=False) for i in range(
                self.texts.shape[0]) if self.texts['type_id'].iloc[i] == self.type_labels['id'][self.selected_type_idx] and (filter_ex in self.texts['title'].iloc[i].lower() or filter_ex in self.texts['author'].iloc[i].lower())]

    def populateList(self):
        self.list_widget.clear()

        for item in self.list_items:
            my_list_widget = QListWidgetItem(self.list_widget)
            # Set size hint
            my_list_widget.setSizeHint(item.sizeHint())
            # Add QListWidgetItem into QListWidget
            self.list_widget.addItem(my_list_widget)
            self.list_widget.setItemWidget(my_list_widget, item)
        # self.list_widget.addItems([f"{grammars['jp'].iloc[i]} | {grammars['en'].iloc[i]}" for i in range(grammars.shape[0])])
        self.list_widget.currentRowChanged.connect(self.rowChanged)

    def getTypesCombinations(self):
        type_tuples = [(self.types['type_id'].iloc[x], self.types['type'].iloc[x])
                       for x in range(self.types.shape[0])]
        type_labels = {'id': [], 'label': []}
        for i in range(len(type_tuples) + 1):
            for subset in itertools.combinations(type_tuples, i):
                if len(subset) > 0:
                    # print(subset)
                    type_labels['id'].append(
                        [subset[i][0] for i in range(len(subset))])
                    label = ''.join(
                        [subset[i][1]+"+" for i in range(len(subset))])
                    type_labels['label'].append(label[:len(label)-1])

        return type_labels

    def randomBtnPressed(self):
        pass

    def rowChanged(self, idx):
        # CHECK THIS PASSES THE CORRECT TEXT INFO EVEN WHEN LIST IS FILTERED (IDX MAY NOT BE DATAFRAME INDEX)
        self.parent().textSelected(self.texts.iloc[idx])


class CharacterInputs(QWidget):
    def __init__(self):
        super().__init__()
        # self.widget = QWidget()
        self.widget_layout = QHBoxLayout()

        self.input_box = QLineEdit()
        self.input_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_box.setObjectName("kanaRaceInputBox")
        self.input_box.setMaxLength(3)
        self.widget_layout.addWidget(self.input_box)

        # self.widget.setLayout(self.widget_layout)

        self.setLayout(self.widget_layout)

    def setFocus(self):
        self.input_box.setFocus()


class CharacterLabel(QWidget):
    def __init__(self, objName, kana=None, romaji=None):
        super().__init__()
        self.kana = kana
        self.romaji = romaji
        self.status = {"not_done": True, "in_progress": False,
                       "incorrect": False, "correct": False}

        self.widget = QWidget()
        self.widget.setObjectName(objName)

        self.widget_label = QLabel(self.kana)
        self.widget_layout = QHBoxLayout()
        self.widget_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.widget_layout.addWidget(self.widget_label)

        self.widget.setLayout(self.widget_layout)

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.widget)

        self.setLayout(self.layout)

    def setKana(self, kana):
        self.kana = kana
        self.widget_label.setText(self.kana)

    def setRomaji(self, romaji):
        self.romaji = romaji

    def getKana(self):
        return self.kana

    def getRomaji(self):
        return self.romaji


class PlayArea(QWidget):
    def __init__(self, level, db, user):
        super().__init__()
        self.level = level
        self.db = db
        self.user = user
        self.started = False
        self.curr_char = 0
        self.curr_line_chars = {"kana": [], "romaji": []}

        self.chars_per_line = 15
        self.current_characters = [CharacterLabel("kanaRaceCharacterLabelCurrent", kana="")
                                   for i in range(self.chars_per_line)]
        self.next_characters = [CharacterLabel("kanaRaceCharacterLabelNextPrevious", kana="")
                                for i in range(self.chars_per_line)]
        self.previous_characters = [CharacterLabel("kanaRaceCharacterLabelNextPrevious", kana="")
                                    for i in range(self.chars_per_line)]
        self.current_inputs = [CharacterInputs()
                               for i in range(self.chars_per_line)]

        self.text_selected = False

        self.container = QHBoxLayout()

        self.select_text_field = SelectTextField(self.db, self.user)

        self.play_container = QVBoxLayout()

        self.text_title_container = QHBoxLayout()

        self.text_title_label = QLabel('-')
        self.text_title_label.setObjectName("textTitleLabel")

        self.personal_best_label = QLabel('')
        self.personal_best_label.setObjectName("personalBestLabel")

        self.text_title_container.addWidget(self.text_title_label)
        self.text_title_container.addWidget(self.personal_best_label)

        self.play_container.addLayout(self.text_title_container)

        self.race_info_buttons_container = QHBoxLayout()

        self.timer_label = QLabel("--:--")
        self.timer_label.setObjectName("timer")

        self.chars_remaining_label = QLabel("-")

        self.chars_icon = QLabel(self)
        pixmap = QPixmap(r"assets/images/character_icon.png").scaled(15, 15)
        self.chars_icon.setPixmap(pixmap)

        self.play_button = PlayButton()

        self.reset_button = ResetButton()

        self.race_info_buttons_container.addWidget(self.timer_label)
        self.race_info_buttons_container.addWidget(self.chars_icon)
        self.race_info_buttons_container.addWidget(self.chars_remaining_label)
        self.race_info_buttons_container.addStretch(1)
        self.race_info_buttons_container.addWidget(self.reset_button)
        self.race_info_buttons_container.addWidget(self.play_button)

        self.play_container.addLayout(self.race_info_buttons_container)

        self.text_widget = QWidget()

        self.text_container = QVBoxLayout()
        self.text_container.setContentsMargins(0, 0, 0, 0)
        self.text_container.setAlignment(
            Qt.AlignmentFlag.AlignLeft)

        # self.input_box = QLineEdit()
        # self.input_box.setObjectName("kanaRaceInput")
        # self.input_box.textEdited.connect(self.textInputted)

        self.previous_line_container = QHBoxLayout()
        self.next_line_container = QHBoxLayout()

        self.current_line_container = QVBoxLayout()
        self.current_line_character_container = QHBoxLayout()
        self.current_line_character_container.setContentsMargins(0, 0, 0, 0)
        # self.current_line_character_container.setAlignment(
        #     Qt.AlignmentFlag.AlignLeft)
        self.current_line_input_container = QHBoxLayout()
        self.current_line_input_container.setContentsMargins(0, 0, 0, 0)
        # self.current_line_input_container.setAlignment(
        #     Qt.AlignmentFlag.AlignLeft)
        for i in range(self.chars_per_line):
            self.current_line_character_container.addWidget(
                self.current_characters[i])
            self.current_line_input_container.addWidget(
                self.current_inputs[i])

            self.previous_line_container.addWidget(self.previous_characters[i])
            self.next_line_container.addWidget(self.next_characters[i])

        self.current_line_container.addLayout(
            self.current_line_character_container)
        self.current_line_container.addLayout(
            self.current_line_input_container)

        self.text_container.addLayout(self.previous_line_container)
        self.text_container.addLayout(self.current_line_container)
        self.text_container.addLayout(self.next_line_container)

        # self.jp_line_previous = QLabel("")
        # self.jp_line_previous.setObjectName("kanaRacePreviousLine")
        # self.previous_line_widget = QWidget()
        # self.previous_line_widget.setObjectName("kanaRaceLineWidget")
        # self.previous_line_widget_layout = QHBoxLayout()
        # self.previous_line_widget_layout.addWidget(self.jp_line_previous)
        # self.previous_line_widget.setLayout(self.previous_line_widget_layout)

        # self.jp_line_current = QLabel("")
        # self.jp_line_current.setObjectName("kanaRaceCurrentLine")
        # self.current_line_widget = QWidget()
        # self.current_line_widget.setObjectName("kanaRaceLineWidget")
        # self.current_line_widget_layout = QHBoxLayout()
        # self.current_line_widget_layout.addWidget(self.jp_line_current)

        # self.jp_line_current = [CharacterLabel()
        #                         for i in range(self.chars_per_line)]

        # for i in self.jp_line_current:
        #     self.current_line_widget_layout.addWidget(i)
        # self.current_line_widget.setLayout(self.current_line_widget_layout)

        # self.jp_line_next = QLabel("")
        # self.jp_line_next.setObjectName("kanaRaceNextLine")
        # self.next_line_widget = QWidget()
        # self.next_line_widget.setObjectName("kanaRaceLineWidget")
        # self.next_line_widget_layout = QHBoxLayout()
        # self.next_line_widget_layout.addWidget(self.jp_line_next)
        # self.next_line_widget.setLayout(self.next_line_widget_layout)

        # self.text_container.addWidget(self.previous_line_widget)
        # self.text_container.addWidget(self.current_line_widget)
        # self.text_container.addWidget(self.input_box)
        # self.text_container.addWidget(self.next_line_widget)

        self.text_widget.setLayout(self.text_container)

        # self.play_container.addLayout(self.text_container)
        self.play_container.addWidget(self.text_widget)

        self.container.addLayout(self.play_container)

        self.container.addWidget(self.select_text_field)

        self.setLayout(self.container)

    def textInputted(self, text):
        pass

    def textSelected(self, text_info):
        self.curr_char = 0
        self.text_selected = True
        self.text_title = text_info['title']
        self.text_author = text_info['author']
        self.text_length = text_info['length']

        self.text_title_label.setText(self.text_title)
        self.chars_remaining_label.setText(str(self.text_length))

        with open(r"assets\texts\Triumphant Return Festival#Kyoka Izumi#hiragana#6702.txt", "r", encoding="utf-16") as f:
            self.text = f.read()

        self.setLines()

    def setLines(self):

        # Previous characters
        if not self.curr_line_chars['kana'] == []:
            for i in range(len(self.curr_line_chars['kana'])):
                self.previous_characters[i].setKana(
                    self.curr_line_chars['kana'])

        # Current characters
        if self.curr_char == 0:  # If this is the first line, there will be no "next characters" to become the current characters
            new_line = self.text[self.curr_char:min(
                self.curr_char+self.chars_per_line, self.text_length)]
        else:
            new_line = "".join(
                map(lambda x: x.getKana(), self.next_characters))

        self.convertToRomaji(new_line)
        for i in range(len(self.curr_line_chars['kana'])):
            self.current_characters[i].setKana(
                self.curr_line_chars['kana'][i])
            self.current_characters[i].setRomaji(
                self.curr_line_chars['romaji'][i])

        # Next characters
        for i in range(self.curr_char+len(self.curr_line_chars['kana']), min(self.text_length, self.curr_char+len(self.curr_line_chars['kana'])+self.chars_per_line)):
            print(i)
            print(i-self.curr_char)
            print(self.text[i])
            self.next_characters[i-(self.curr_char +
                                    len(self.curr_line_chars['kana']))].setKana(self.text[i])

        self.current_inputs[0].setFocus()

    def convertToRomaji(self, text):
        kks = pykakasi.kakasi()
        # text = "紫の幕、くれないの旗、空の色の青く晴れたる"
        small_tsu = False
        for char in text:
            convert = kks.convert(char)

            if small_tsu and char != "、" and char != "。" and char != "「" and char != "」":
                char = "っ" + char
                small_tsu = False
            if convert[0]['orig'] == "っ" or convert[0]['orig'] == "ッ":
                small_tsu = True
                pass
            else:
                self.curr_line_chars["kana"].append(
                    kks.convert(char)[0]['orig'])
                self.curr_line_chars["romaji"].append(
                    kks.convert(char)[0]['hepburn'])

    def startTimer(self):
        pass

    def stopTimer(self):
        pass


class KanaRacePage(QWidget):
    def __init__(self, level):
        super().__init__()
        self.level = level
        self.user = 1
        self.db = Database()

        self.text_types = self.db.get_text_types()
        self.texts = self.db.get_texts_all()

        self.container = QVBoxLayout()

        self.title_bar_layout = QHBoxLayout()
        self.title_bar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title = tools.getPageTitle(self.level, "Kana Race")
        self.title.setObjectName("pageTitle"+self.level)
        self.title_bar_layout.addWidget(self.title)

        self.container.addLayout(self.title_bar_layout)

        self.play_area = PlayArea(self.level, self.db, self.user)
        self.container.addWidget(self.play_area)

        self.setLayout(self.container)
