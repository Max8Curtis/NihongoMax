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
from os import path
import random

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
from assets.tools import Tools, Time
tools = Tools()
time = Time()

styles = "assets\styles\styles.css"


class MyQLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()

    keyPressed = QtCore.pyqtSignal(int)

    def keyPressEvent(self, event):
        super(QLineEdit, self).keyPressEvent(event)
        self.keyPressed.emit(event.key())


class QCustomTextListWidget(QCustomListWidget):
    def __init__(self, idx, jp, en, selected, pb, author, length, parent=None):
        super().__init__(idx, jp, en, selected, parent)
        self.pb = pb
        self.author = author
        self.length = length
        self.updateText()
        # self.en_text.setText(f"{self.author} - Length: {self.length} - PB: {time.secondsToMinutesSeconds(self.pb)}")

    def clicked(self):
        pass

    def updatePb(self, pb):
        self.pb = pb
        self.updateText()

    def updateText(self):
        self.en_text.setText(
            f"{self.author} - Length: {self.length} - PB: {time.secondsToMinutesSeconds(self.pb) if not time.secondsToMinutesSeconds(self.pb) is None else '--:--'}")


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
        self.parent().resetBtnPressed()


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
        # self.started = not self.started
        if self.started:
            self.displayPlayIcon()
            self.parent().stopTimer()
        else:
            self.displayPauseIcon()
            self.parent().playButtonPressed()

    def displayPlayIcon(self):
        self.started = False
        pixmap = QPixmap(r"assets/images/play.png").scaled(15, 15)
        self.button_icon.setPixmap(pixmap)

    def displayPauseIcon(self):
        self.started = True
        pixmap = QPixmap(r"assets/images/pause.png").scaled(15, 15)
        self.button_icon.setPixmap(pixmap)

    def getStarted(self):
        return self.started

    def reset(self):
        self.displayPlayIcon()


class SelectTextField(QWidget):
    def __init__(self, db, user, parent):
        super(SelectTextField, self).__init__(parent)
        self.db = db
        self.user = user

        self.types = self.db.get_text_types()
        # self.types = types
        self.texts = self.db.get_user_texts(user)
        # print(self.texts)
        self.selected_type_idx = 0

        self.type_labels = self.getTypesCombinations()
        # print(self.type_labels)

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
            # print(text)

        self.populateList()

    def updateTypeSelection(self, index):
        self.selected_type_idx = index
        self.filterListItems()
        self.populateList()

    def filterListItems(self, filter_ex=None):
        # TODO:
        #  Add sophisticated searching and order list items by similarity to the search text
        ##
        if filter_ex is None:
            self.list_items = [QCustomTextListWidget(idx=self.texts['id'].iloc[i], jp=self.texts['title'].iloc[i], en="", author=self.texts['author'].iloc[i], length=self.texts['length'].iloc[i], selected=False, pb=self.texts['pb'].iloc[i]) for i in range(
                self.texts.shape[0]) if self.texts['type_id'].iloc[i] == self.type_labels['id'][self.selected_type_idx]]
        else:
            filter_ex = filter_ex.lower()
            self.list_items = [QCustomTextListWidget(idx=self.texts['id'].iloc[i], jp=self.texts['title'].iloc[i], en="", author=self.texts['author'].iloc[i], length=self.texts['length'].iloc[i], selected=False, pb=self.texts['pb'].iloc[i]) for i in range(
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
        # Can only randomly select if there is at least one text shown in list
        if len(self.list_items) > 0:
            random_id = random.randint(0, len(self.list_items)-1) # Only select randomly from items currently being shown
            self.list_widget.setCurrentRow(random_id)
            self.rowChanged(random_id)

    def rowChanged(self, idx):
        # idx is the index of the selected row in the list view widget, not the text's id
        
        # idx is -1 when no item is selected, so when the list is refreshed when the type is changed, the 'current row' changes to None
        if not idx == -1:
            # Pass selected text information to parent
            print(self.texts)
            print(idx)
            print(f"{self.texts['id']}, {self.list_items[idx].getIdx()}")
            self.parent().textSelected(
                self.texts[self.texts['id'] == self.list_items[idx].getIdx()])

    def updateTextPB(self, idx, pb):
        # Update the PB displayed on screen for text with ID idx
        # Necessary so that new PBs can be shown on screen without reloading the page
        print(self.texts)
        print(pb)
        print(idx)
        self.texts.loc[self.texts['id'] == idx, 'pb'] = pb
        for i in range(len(self.list_items)):
            if self.list_items[i].getIdx() == idx:
                self.list_items[i].updatePb(pb)


class GameEndDialog(QDialog):
    def __init__(self, time, pb=False):
        super().__init__()

        self.setWindowTitle("Completed")

        QBtn = (
            QDialogButtonBox.StandardButton.Ok
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        layout = QVBoxLayout()
        if pb:
            message = QLabel(f"New personal best achieved! {time}!")
        else:
            message = QLabel(f"おしい! Not quite a personal best!")
        layout.addWidget(message)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


class CustomLineEdit(QLineEdit):
    keyPressed = QtCore.pyqtSignal(int, int)

    def __init__(self, idx):
        super().__init__()
        self.idx = idx

    def keyPressEvent(self, event):
        # print(event.key())
        # print(self.idx)
        self.keyPressed.emit(event.key(), self.idx)
        super(CustomLineEdit, self).keyPressEvent(event)


class CharacterInputs(QWidget):
    transmit = QtCore.pyqtSignal(int, int)

    def __init__(self, idx, parent):
        super(CharacterInputs, self).__init__(parent)
        self.idx = idx
        self.focused = False

        # self.widget = QWidget()
        # print(f"Input parent: {self.parent()}")
        self.widget_layout = QHBoxLayout()

        self.input_box = CustomLineEdit(self.idx)
        self.input_box.setEnabled(False)
        self.input_box.keyPressed.connect(self.onKey)
        self.input_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_box.setObjectName("kanaRaceInputBox")
        self.input_box.textEdited.connect(self.input)
        self.input_box.setMaxLength(1)
        self.widget_layout.addWidget(self.input_box)

        # self.widget.setLayout(self.widget_layout)

        self.setLayout(self.widget_layout)

    def setFocused(self, focus):
        self.focused = focus
        # Input is usable only if it has focus i.e. is the current character being written
        self.input_box.setEnabled(self.focused)
        if self.focused:
            self.input_box.setFocus()

    def onKey(self, key, idx):
        self.transmit.emit(key, idx)
        # print(key)
        # print(idx)

    # def keyPressEvent(self, event):
    #     print(f"key: {event.key()}")
    #     # super(CharacterInputs, self).keyPressEvent(event)
    #     # self.parent().parent().onKey(event.key(), self.idx)
    #     self.keyPressed.emit(event.key(), self.idx)

    def input(self, t):
        # print(self.parent())
        self.parent().parent().textInput(self.idx, t)

    # def setFocus(self):
    #     self.input_box.setFocus()

    def setMaxLength(self, length):
        self.input_box.setMaxLength(length)

    def getMaxLength(self):
        return self.input_box.maxLength()

    def getText(self):
        return self.input_box.text()

    def clear(self):
        self.input_box.clear()


class CharacterLabel(QWidget):
    def __init__(self, objName, kana=None, romaji=None):
        super().__init__()
        self.objName = objName
        self.kana = kana
        self.romaji = romaji
        self.status = {"not_done": True, "in_progress": False,
                       "incorrect": False, "correct": False}

        self.widget = QWidget()
        self.widget.setObjectName(self.objName)

        self.widget_label = QLabel(self.kana)
        self.setKana(self.kana)

        self.widget_layout = QHBoxLayout()
        self.widget_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.widget_layout.addWidget(self.widget_label)

        self.widget.setLayout(self.widget_layout)

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.widget)

        self.setLayout(self.layout)

    def updateStyle(self, status):
        self.widget_label.setObjectName("kanaRaceCharacterLabelCurrent"+status)
        # self.widget.setObjectName(self.objName+status)

        style = self.widget_label.style()
        style.unpolish(self.widget_label)
        style.polish(self.widget_label)
        self.widget_label.update()

    def setKana(self, kana):
        # print(self.parent())
        self.kana = kana
        self.widget_label.setText(self.kana)

    def setRomaji(self, romaji):
        self.romaji = romaji

    def getKana(self):
        return self.kana

    def getRomaji(self):
        return self.romaji

    def reset(self):
        self.setKana("")
        self.setRomaji("")
        self.updateStyle("")


class PlayArea(QWidget):
    def __init__(self, level, db, user):
        super(PlayArea, self).__init__()
        self.level = level
        self.db = db
        self.user = user
        self.started = False
        self.curr_char = 0
        self.curr_selected_char = 0
        self.text_selected = False
        self.text_title = None
        self.text_author = None
        self.text_length = None
        self.time = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateTimer)
        self.curr_line_chars = {"kana": [], "romaji": []}

        self.chars_per_line = 15

        self.current_characters = [CharacterLabel("kanaRaceCharacterLabelWidgetCurrent", kana="")
                                   for i in range(self.chars_per_line)]
        self.next_characters = [CharacterLabel("kanaRaceCharacterLabelWidgetNextPrevious", kana="")
                                for i in range(self.chars_per_line)]
        self.previous_characters = [CharacterLabel("kanaRaceCharacterLabelWidgetNextPrevious", kana="")
                                    for i in range(self.chars_per_line)]
        self.current_inputs = [CharacterInputs(i, self)
                               for i in range(self.chars_per_line)]
        for i in range(self.chars_per_line):
            self.current_inputs[i].transmit.connect(self.onKey)

        self.text_selected = False

        self.container = QHBoxLayout()

        self.select_text_field = SelectTextField(self.db, self.user, self)

        self.play_container = QVBoxLayout()
        self.play_container.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.text_title_container = QVBoxLayout()

        self.text_title_label = QLabel('-')
        self.text_title_label.setToolTip('Text title')
        self.text_title_label.setObjectName("textTitleLabel")

        self.author_label = QLabel('-')
        self.author_label.setToolTip('Text author')
        self.author_label.setObjectName("authorLabel")

        self.personal_best_label = QLabel('')
        self.personal_best_label.setToolTip('Personal best')
        self.personal_best_label.setObjectName("personalBestLabel")

        self.text_title_container.addWidget(self.text_title_label)
        self.text_title_container.addWidget(self.author_label)
        self.text_title_container.addWidget(self.personal_best_label)

        self.play_container.addStretch(2)
        self.play_container.addStretch(2)
        self.play_container.addLayout(self.text_title_container)
        self.play_container.addStretch(1)

        self.race_info_buttons_container = QHBoxLayout()

        self.timer_label = QLabel("--:--")
        self.timer_label.setObjectName("timer")

        self.chars_remaining_label = QLabel("-")
        self.chars_remaining_label.setToolTip("Number of characters remaining")

        self.chars_icon = QLabel(self)
        self.chars_remaining_label.setToolTip("Number of characters remaining")
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

        # self.text_widget = TextWidget(self.chars_per_line,
        #   self.current_characters, self.previous_characters, self.next_characters, self.current_inputs)

        self.text_widget = QWidget()
        self.text_container = QVBoxLayout()
        self.text_container.setContentsMargins(-5, -5, -5, -5)
        self.text_container.setSpacing(0)
        self.text_container.setAlignment(
            Qt.AlignmentFlag.AlignLeft)

        self.previous_line_container = QHBoxLayout()
        self.next_line_container = QHBoxLayout()

        self.current_line_container = QVBoxLayout()
        self.current_line_character_container = QHBoxLayout()
        self.current_line_character_container.setContentsMargins(
            -5, -5, -5, -5)
        # self.current_line_character_container.setAlignment(
        #     Qt.AlignmentFlag.AlignLeft)
        self.current_line_input_container = QHBoxLayout()
        self.current_line_input_container.setContentsMargins(-5, -5, -5, -5)
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

        self.text_widget.setLayout(self.text_container)
        self.play_container.addStretch(1)
        # self.play_container.addLayout(self.text_container)
        self.play_container.addWidget(self.text_widget)
        self.play_container.addStretch(1)

        self.container.addLayout(self.play_container)

        self.container.addWidget(self.select_text_field)

        self.setLayout(self.container)

    def onKey(self, key, idx):
        if key == Qt.Key.Key_Backspace:
            if self.current_inputs[idx].getText() == "" and idx > 0:
                # Return current label to default styling
                self.current_characters[idx].updateStyle("")
                # Move focus to previous input
                self.current_inputs[idx-1].setFocused(True)
                self.current_inputs[idx].setFocused(False)
                self.curr_char -= 1
                self.updateCharactersRemaining()

    def textInput(self, idx, text):
        if not self.play_button.getStarted():
            # self.started = not self.started
            self.startTimer()
            self.play_button.displayPauseIcon()
        # Update label styling based on if the current input is correct so far
        if text != self.current_characters[idx].getRomaji()[:len(text)]:
            self.current_characters[idx].updateStyle("Incorrect")
        else:
            self.current_characters[idx].updateStyle("Selected")
        # If the text written so far is the length of the correct romaji, change styling and move focus to next character
        if len(text) == self.current_inputs[idx].getMaxLength():
            # If text is correct
            if text == self.current_characters[idx].getRomaji():
                self.current_characters[idx].updateStyle("Correct")
                if self.curr_char == self.text_length-1:  # The end ofthe text has been reached
                    self.end()
                else:
                    # This executes if the end of the line has been reached
                    if idx == len(self.curr_line_chars['kana'])-1:
                        for i in range(len(self.current_inputs)):
                            self.current_inputs[i].clear()
                        self.current_inputs[0].setFocused(True)
                        self.current_inputs[idx].setFocused(False)
                        # Increment current char tracker then set new lines so that next line starts with character immediately after current line
                        self.curr_char += 1
                        self.setLines()
                    else:  # If the current character is not the last on the line, move focus to next character
                        self.current_inputs[idx+1].setFocused(True)
                        self.current_inputs[idx].setFocused(False)
                        self.current_characters[idx+1].updateStyle("Selected")
                        self.curr_char += 1

                    self.updateCharactersRemaining()

        print(self.curr_char)

    def end(self):
        self.stopTimer()
        # Get current time on timer
        time_taken = self.timer_label.text()
        print(time_taken)
        # Convert time string to seconds for comparison with current PB
        seconds = time.minutesSecondsToSeconds(time_taken)
        print(seconds)
        # If current time is faster than PB update the users PB
        print(f"Text pb: {self.text_pb}")
        if seconds < self.text_pb or pd.isna(self.text_pb):
            print("New PB!")
            dlg = GameEndDialog(time_taken, pb=True)
            self.db.update_user_text_pb(
                user=1, text=self.text_id, time=seconds)
            user_text_info = self.db.get_user_text_info(
                self.user, self.text_id)
            print(user_text_info)
            self.select_text_field.updateTextPB(
                user_text_info['text_id'].iloc[0], user_text_info['pb'].iloc[0])
            self.personal_best_label.setText(
                time.secondsToMinutesSeconds(user_text_info['pb']))
        else:
            dlg = GameEndDialog(time_taken, pb=False)
        dlg.exec()

        self.reset()
        self.setLines()

    def updateCharactersRemaining(self):
        if not self.text_length is None:
            self.chars_remaining_label.setText(
                str(self.text_length-self.curr_char))

    def textSelected(self, text_info):
        self.reset()
        self.curr_char = 0
        self.text_selected = True
        self.text_id = text_info['id'].iloc[0]
        self.text_title = text_info['title'].iloc[0]
        self.text_author = text_info['author'].iloc[0]
        self.text_length = text_info['length'].iloc[0]
        self.text_pb = text_info['pb'].iloc[0]

        self.text_title_label.setText(self.text_title)
        self.author_label.setText(self.text_author)
        self.personal_best_label.setText(
            time.secondsToMinutesSeconds(self.text_pb))

        self.chars_remaining_label.setText(str(self.text_length))
        texts_dir = "assets\\texts"
        texts_path = path.join(
            texts_dir, f"{self.text_title}#{self.text_author}#hiragana#{self.text_length}.txt")
        with open(fr"{texts_path}", "r", encoding="utf-16") as f:
            self.text = f.read()

        self.setLines()

    def setLines(self):
        # Previous characters
        if not self.curr_line_chars['kana'] == []:
            # # Increment current character tracker so that the next line is populated following on from current line
            # self.curr_char += len(self.curr_line_chars['kana'])
            for i in range(len(self.curr_line_chars['kana'])):
                print(i)
                self.previous_characters[i].setKana(
                    self.curr_line_chars['kana'][i])

        self.curr_line_chars['kana'] == []
        self.curr_line_chars['romaji'] == []

        # Current characters
        if self.curr_char == 0:  # If this is the first line, there will be no "next characters" to become the current characters
            new_line = self.text[self.curr_char:min(
                self.curr_char+self.chars_per_line, self.text_length)]
        else:
            new_line = "".join(
                map(lambda x: x.getKana(), self.next_characters))

        print(new_line)

        # Converts the kana line to romaji and sets the current line dictionary
        self.convertToRomaji(new_line)
        print(self.curr_line_chars)
        for i in range(len(self.curr_line_chars['kana'])):
            self.current_characters[i].setKana(
                self.curr_line_chars['kana'][i])
            self.current_characters[i].setRomaji(
                self.curr_line_chars['romaji'][i])
            # Set the max number of characters for ith input box to the number of romaji characters in ith label (so that input cannnot be longer than the answer)
            self.current_inputs[i].setMaxLength(
                len(self.curr_line_chars['romaji'][i]))
            # Return current characters to default style
            self.current_characters[i].updateStyle("")

        # Incase there are unused spaces on the current line, set the excess spaces to blank
        for i in range(len(self.curr_line_chars['kana']), self.chars_per_line):
            self.current_characters[i].setKana("")
            self.current_characters[i].setRomaji("")
            # Set the max number of characters for ith input box to the number of romaji characters in ith label
            self.current_inputs[i].setMaxLength(0)

        # Next characters
        # If there are unused character spaces on the current line, then this is the final line of the text, so the next line should be blank
        if len(self.curr_line_chars['kana']) < self.chars_per_line:
            for i in range(len(self.next_characters)):
                self.next_characters[i].reset()
        else:  # The current line is not the final line, so populate the next line
            for i in range(self.curr_char+len(self.curr_line_chars['kana']), min(self.text_length, self.curr_char+len(self.curr_line_chars['kana'])+self.chars_per_line)):
                self.next_characters[i-(self.curr_char +
                                        len(self.curr_line_chars['kana']))].setKana(self.text[i])

        self.current_inputs[0].setFocused(True)
        self.current_characters[0].updateStyle("Selected")

    def convertToRomaji(self, text):
        kks = pykakasi.kakasi()
        self.curr_line_chars["kana"] = []
        self.curr_line_chars["romaji"] = []
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

    def resetCharacterClasses(self):
        for i in range(self.chars_per_line):
            self.previous_characters[i].setKana("")
            self.current_characters[i].setKana("")
            self.next_characters[i].setKana("")
            self.current_inputs[i].clear()

    def reset(self):
        self.curr_char = 0
        self.updateCharactersRemaining()
        self.stopTimer()
        self.time = 0

        self.updateTimerLabel()
        self.play_button.reset()
        self.curr_selected_char = 0
        self.curr_line_chars = {"kana": [], "romaji": []}
        self.resetCharacterClasses()

    def resetBtnPressed(self):
        self.reset()
        self.setLines()

    def stopTimer(self):
        self.timer.stop()

    def playButtonPressed(self):
        self.startTimer()
        self.current_inputs[self.curr_char %
                            len(self.curr_line_chars['kana'])].setFocused(True)

    def startTimer(self):
        # self.started = True
        self.timer.start(1000)
        self.updateTimerLabel()

    def updateTimer(self):
        self.time += 1
        self.updateTimerLabel()
        return None

    def updateTimerLabel(self):
        formatted_time = time.secondsToMinutesSeconds(self.time)

        self.timer_label.setText(formatted_time)


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
