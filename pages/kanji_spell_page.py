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

class QCustomListWidget(QCustomListWidget):
    def __init__ (self, idx, jp, en, selected, parent = None):
        super(QCustomListWidget, self).__init__(idx, jp, en, selected, parent)


    def updateStyle(self):
        pass

    def clicked(self):
        pass    

    def setSelected(self, s):
        pass     
            
    def getSelected(self):
        pass

    def getIdx(self):
        pass

class CustomDialog(QDialog):
    def __init__(self, incorrect_words, num_unanswered):
        super().__init__()
        self.incorrect_words = incorrect_words
        self.num_unanswered = num_unanswered
        print(f"Num unanswered: {self.num_unanswered}")
        print("Incorrect words: ")
        print(self.incorrect_words)

        self.setWindowTitle("Mistake report")

        QBtn = (
            QDialogButtonBox.StandardButton.Ok
        )

        self.button_box = QDialogButtonBox(QBtn)
        self.button_box.accepted.connect(self.accept)
        # self.buttonBox.rejected.connect(self.reject)
        if self.num_unanswered > 0:
            if self.num_unanswered == 1:
                unanswered_message = QLabel(f"おそい！ {self.num_unanswered} word was left unanswered!")
            else:
                unanswered_message = QLabel(f"おそい！ {self.num_unanswered} words were left unanswered!")
        else:
            unanswered_message = QLabel(f"はやい！ You answered all the words!")

        layout = QVBoxLayout()
        if self.incorrect_words.empty:
            message = QLabel("No mistakes, well done!")
            layout.addWidget(message)
            layout.addWidget(unanswered_message)
        else:
            message = QLabel("Some words were incorrect, have a look!")
            layout.addWidget(message)
            layout.addWidget(unanswered_message)
            list_widget = QListWidget()
            list_items = [QCustomListWidget(idx=None, jp=f"{self.incorrect_words['ka'].iloc[i]} | {self.incorrect_words['hg'].iloc[i]}", en=self.incorrect_words['en'].iloc[i], selected=None) for i in range(self.incorrect_words.shape[0])]
            for item in list_items:
                my_list_widget = QListWidgetItem(list_widget)
                # Set size hint
                my_list_widget.setSizeHint(item.sizeHint())
                # Add QListWidgetItem into QListWidget
                list_widget.addItem(my_list_widget)
                list_widget.setItemWidget(my_list_widget, item)
            layout.addWidget(list_widget)
        layout.addWidget(self.button_box)
        self.setLayout(layout)


class MyQLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()

    keyPressed = QtCore.pyqtSignal(int)

    def keyPressEvent(self, event):
        super(QLineEdit, self).keyPressEvent(event)
        self.keyPressed.emit(event.key())

class PlayArea(QWidget):
    def __init__(self, words, level):
        super().__init__()
        self.words = words
        self.level = level
        self.started = False
        self.words['selected'] = [False for i in range(self.words.shape[0])]
        self.answer_submitted = False
        self.current = 0
        self.display_en = False
        self.kanji_fontsize = 50
        self.english_fontsize = 20
        self.answer_fontsize = 32
        self.timer_fontsize = 16
        self.questions_counter_fontsize = 16
        self.current_text_hg = ""
        self.convert = Convert()
        self.kks = pykakasi.kakasi()
        self.time_limit = 1
        
        self.colors = Color()

        self.container = QHBoxLayout()
    
        self.options_container = QHBoxLayout()
        self.options_grid = QGridLayout()

        self.options_label = QLabel('Options:')
        self.options_label.setObjectName("optionsLabel")
        # self.setFontSize(self.options_label, 20)
        self.options_container.addWidget(self.options_label)
        self.options_container.addStretch(1)

        self.spin_box = QSpinBox(self)
        self.spin_box.setObjectName("timeSelectSpinBox")
        self.spin_box.setRange(0, 600)  # Set the range of values
        self.spin_box.setValue(1)

        self.loop_radio = QRadioButton('Loop', self)
        self.loop_radio.setObjectName("kanjiSpellOption")
        self.loop_radio.setChecked(True)
        
        self.timer_radio = QRadioButton('Timer (seconds)', self)
        self.timer_radio.toggled.connect(self.timerRadioToggled)
        self.timer_radio.setObjectName("kanjiSpellOption")
        self.spin_box.setEnabled(False)
        # self.spin_box.setStyleSheet("""background: #e8e8e5;""")

        self.remove_seconds_button = QPushButton('-10s')
        self.remove_seconds_button.setEnabled(False)
        self.remove_seconds_button.clicked.connect(self.removeSeconds)
        # self.remove_seconds_button.setProperty("class", "button")
        self.remove_seconds_button.setObjectName("changeTimerButton")
        # self.remove_seconds_button.setMaximumWidth(40)
        self.remove_seconds_button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

        self.add_seconds_button = QPushButton('+10s')
        self.add_seconds_button.setEnabled(False)
        self.add_seconds_button.clicked.connect(self.addSeconds)
        # self.add_seconds_button.setProperty("class", "button")
        self.add_seconds_button.setObjectName("changeTimerButton")
        # self.add_seconds_button.setMaximumWidth(40)
        self.add_seconds_button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

        self.toggle_english_checkbox = QCheckBox('Display English')
        self.toggle_english_checkbox.setObjectName("kanjiSpellOption")
        self.toggle_english_checkbox.stateChanged.connect(self.englishToggled)

        self.options_grid.addWidget(self.loop_radio, 1, 1)
        self.options_grid.addWidget(self.timer_radio, 2, 1)   
        self.options_grid.addWidget(self.spin_box, 2, 2)
        self.options_grid.addWidget(self.add_seconds_button, 2, 3)
        self.options_grid.addWidget(self.remove_seconds_button, 2, 4)
        self.options_grid.addWidget(self.toggle_english_checkbox, 3, 1)

        self.options_grid.setColumnMinimumWidth(2, 100)
        # self.options_grid.setColumnStretch(3, 1)
        # self.options_grid.setColumnStretch(5, 1)
        self.options_grid.setColumnStretch(0, 1)
        self.options_grid.setRowStretch(0,1)
        self.options_grid.setRowStretch(4,1)

        self.start_button = StartButton()
        # self.options_grid.addWidget(self.start_button, 2, 5)

        self.options_container.addLayout(self.options_grid)

        self.options_container.addStretch(2)

        self.options_play_area_container = QVBoxLayout()

        self.options_play_area_container.addLayout(self.options_container)

        # self.play_area_container = QGridLayout()
        # self.play_area_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.kanji_label = QLabel('--')
        # self.setFontSize(self.kanji_label, self.kanji_fontsize)
        # self.kanji_label.setToolTip(None)
        self.kanji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.kanji_label.setStyleSheet("""background: rgba(0,0,0,0)""")
        self.kanji_label.setObjectName("kanjiSpellKanjiLabel")

        self.english_label = QLabel('')
        self.english_label.setWordWrap(True)
        self.english_label.setObjectName("kanjiSpellEnglishLabel")
        # self.english_label.setMaximumWidth(270)
        # self.english_label.setMinimumHeight(100)
        self.english_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.english_label.setStyleSheet("""background: rgba(0,0,0,0)""")
        # self.setFontSize(self.english_label, self.english_fontsize)

        self.answer_label = QLabel('')
        self.answer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.answer_label.setObjectName("kanjiSpellAnswerLabel")
        # self.answer_label.setStyleSheet("""background: rgba(0,0,0,0)""")
        # self.setFontSize(self.answer_label, self.answer_fontsize)

        self.answer_layout = QHBoxLayout()
        self.answer_layout.addStretch(1)
        self.answer_input = QLineEdit()
        self.answer_input.setObjectName("kanjiSpellAnswerInput")
        self.answer_input.setMaxLength(15)
        self.answer_input.returnPressed.connect(self.enterBtnPressed)
        # self.answer_input.setProperty("class", "answerInput")
        self.answer_input.setAlignment(Qt.AlignmentFlag.AlignCenter)              # <-----
        self.answer_input.textEdited.connect(self.textInputted)
        # self.answer_input.setStyleSheet("""background: rgba(247, 247, 247, 1)""")
        # self.setFontSize(self.answer_input, 14)
        self.answer_layout.addWidget(self.answer_input)

        self.enter_button = QPushButton()
        self.enter_button.setObjectName("kanjiSpellEnterButton")
        # self.enter_button.setMinimumHeight(60)
        # self.enter_button.setMinimumWidth(80)
        # self.enter_button.setMaximumWidth(100)
        self.enter_button_layout = QHBoxLayout()
        self.enter_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.enter_label = QLabel('Enter')
        # self.enter_label.setStyleSheet("""background: rgba(0,0,0,0)""")
        # self.setFontSize(self.enter_label, 14)
        self.enter_button_layout.addWidget(self.enter_label)
        self.enter_button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        # self.enter_button.setProperty("class", "button")
        self.enter_button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.enter_button.setLayout(self.enter_button_layout)
        self.enter_button.setDefault(False)
        self.enter_button.pressed.connect(self.enterBtnPressed)
        # self.enter_button.setStyleSheet("""
        #                                 QPushButton {
        #                                     background: white;
        #                                 }
        #                                 QPushButton:hover {
        #                                     background: #CCF4FF;
        #                                 }""")
        self.answer_layout.addWidget(self.enter_button)
        self.answer_layout.addStretch(1)

        self.timer_layout = QVBoxLayout()
        self.timer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label_default_text = "--:--"
        self.timer_title = QLabel("Time remaining:")
        self.timer_title.setObjectName("kanjiSpellGameplayTitle")
        self.timer_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.timer_title.setStyleSheet("""background: rgba(0,0,0,0)""")
        self.timer_label = QLabel(self.timer_label_default_text)
        self.timer_label.setObjectName("kanjiSpellGamplayLabel")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.timer_label.setStyleSheet("""background: rgba(0,0,0,0)""")
        self.timer_layout.addWidget(self.timer_title)
        self.timer_layout.addWidget(self.timer_label)
        # self.setFontSize(self.timer_title, self.timer_fontsize-4)
        # self.setFontSize(self.timer_label, self.timer_fontsize)

        self.questions_counter_layout = QVBoxLayout()
        self.questions_counter_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.questions_counter_default_text = "--/--"
        self.questions_counter_title = QLabel("Questions answered:")
        self.questions_counter_title.setObjectName("kanjiSpellGameplayTitle")
        self.questions_counter_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.questions_counter_title.setStyleSheet("""background: rgba(0,0,0,0)""")
        self.questions_counter_label = QLabel(self.questions_counter_default_text)
        self.questions_counter_label.setObjectName("kanjiSpellGamplayLabel")
        # self.questions_counter_label.setStyleSheet("""background: rgba(0,0,0,0)""")
        self.questions_counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.questions_counter_layout.addWidget(self.questions_counter_title)
        self.questions_counter_layout.addWidget(self.questions_counter_label)
        # self.setFontSize(self.questions_counter_title, self.questions_counter_fontsize-4)
        # self.setFontSize(self.questions_counter_label, self.questions_counter_fontsize)

        self.timer_questions_container = QHBoxLayout()
        self.timer_questions_container.addLayout(self.timer_layout)
        self.timer_questions_container.addStretch(1)
        self.timer_questions_container.addLayout(self.questions_counter_layout)

        self.play_area_container = QVBoxLayout()
        self.play_area_container.addLayout(self.timer_questions_container)
        self.play_area_container.addWidget(self.kanji_label)
        self.play_area_container.addWidget(self.english_label)
        self.play_area_container.addWidget(self.answer_label)
        self.play_area_container.addLayout(self.answer_layout)

        self.play_area_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setObjectName("dummyBackgroundWidget")
        widget.setLayout(self.play_area_container)
        # rgb = tuple(int(self.colors.get_level_color(self.level)[i:i+2], 16) for i in (0, 2, 4))
        # widget.setStyleSheet(f"""
        #     background: rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.25);
        #     border-radius: 3px;

        # """)
        self.options_play_area_container.addWidget(widget)
        self.options_play_area_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.options_play_area_container.addStretch(1)

        self.select_words_container = QVBoxLayout()
        self.select_words_field = SelectWordField(parent=self, words=self.words)
        self.select_words_field.setMaximumWidth(350)

        # widget = QWidget()
        # widget.setObjectName("dummyBackgroundWidget")
        
        self.start_button = StartButton()
        self.select_words_container.addWidget(self.select_words_field)
        self.select_words_container.addWidget(self.start_button)
        # widget.setLayout(self.select_words_container)
        # widget.setMaximumWidth(360)

        self.container.addLayout(self.options_play_area_container)
        # self.container.addWidget(widget)
        self.container.addLayout(self.select_words_container)
        self.container.setContentsMargins(80,0,0,0)

        # self.keyPressed = QtCore.pyqtSignal(int)
        # self.keyPressed.connect(self.onKey)

        # with open(styles, "r") as f:
        #     self.setStyleSheet(f.read())

        self.setLayout(self.container) 

    def startBtnPressed(self):
        chosen_word_ids = self.select_words_field.getChosenWords()
        self.chosen_words = self.words[self.words['id'].isin(chosen_word_ids)]
        print(self.chosen_words)
        self.answer_input.setFocus()
        if self.chosen_words.shape[0] > 0:
            self.started = True
            self.queue = self.chosen_words[['ka', 'hg', 'en']].sample(self.chosen_words.shape[0])
            self.startGame()
        else:
            self.started = False
            self.resetGame()
            self.english_label.setText("Please select some words")
            self.timer = QtCore.QTimer(self)
            self.timer.setInterval(2000)
            self.timer.timeout.connect(self.resetEnglishLabel)
            self.timer.start()


    def resetEnglishLabel(self):
        self.english_label.setText(None)
        self.english_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFontSize(self.english_label, self.english_fontsize)

    def startGame(self):
        self.queue = self.chosen_words[['ka', 'hg', 'en']].sample(self.chosen_words.shape[0])
        self.current = 0
        self.updateQuestionCounterLabel()
        self.incorrect_words = []
        self.enter_button.setAutoDefault(True)
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
        self.gameEnd()
        return None
                
    def resetGame(self):
        self.time_limit = 0
        self.current = 0
        self.game_ended = False
        self.resetEnglishLabel()
        self.resetAnswerLabel()
        self.resetAnswerInput()
        self.resetTimerLabel()
        self.resetKanjiLabel()
        self.enter_button.setDefault(False)
        self.incorrect_words = None
        self.questions_counter_label.setText(self.questions_counter_default_text)
        self.timer_label.setText(self.timer_label_default_text)
        self.started = False

    def updateQuestionCounterLabel(self):
        self.questions_counter_label.setText(f"{self.current}/{self.queue.shape[0]}")
        # self.setFontSize(self.questions_counter_label, self.questions_counter_fontsize)

    def updateTimerLabel(self):
        mins = self.time_limit // 60
        secs = self.time_limit % 60
        if mins == 0 and secs <= 5:
            self.timer_label.setStyleSheet("""
                color: red;
                background: rgba(0,0,0,0);                 
            """)
        else:
            self.timer_label.setStyleSheet("""
                color: black;     
                background: rgba(0,0,0,0);              
            """)
        self.timer_label.setText(f"{'{:02d}'.format(mins)}:{'{:02d}'.format(secs)}")

    def onKey(self, key):
        # Test for back space key pressed
        if key == Qt.Key.Key_Backspace:
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
            print(self.current)
            is_correct = self.checkAnswer(self.queue['hg'].iloc[self.current])
            if is_correct:
                self.answer_input.setObjectName("kanjiSpellAnswerInputCorrect")

                # print("Correct!")
                # # self.answer_label.setText("Correct!")
                # self.answer_input.setStyleSheet("""
                #     min-height: 60px;
                #     min-width: 200px;
                #     background-color: #02ce79;
                #     font-family: 'Arial', sans-serif;
                #     color: white;
                # """)
            else:
                self.answer_input.setObjectName("kanjiSpellAnswerInputIncorrect")
                # print("Incorrect!")
                # # self.answer_label.setText("Not quite!")
                # self.answer_input.setStyleSheet("""
                #     min-height: 60px;
                #     min-width: 200px;
                #     background-color: #e74545;
                #     font-family: 'Arial', sans-serif;
                #     color: white;
                # """)
                # self.answer_label
                # self.incorrect_words.append(self.current)
            style = self.answer_input.style()
            style.unpolish(self.answer_input)
            style.polish(self.answer_input)
            self.answer_input.update()
            
            # self.setFontSize(self.answer_label, self.answer_fontsize)
            self.answer_timer = QtCore.QTimer(self)
            # self.answer_timer.setInterval(750)
            self.answer_timer.timeout.connect(self.resetAnswerInput)
            self.answer_timer.start(750)
            self.answer_input.setText(None)
            self.current_text_hg = ""
            self.answer_label.setText(None)
            self.current += 1
            self.updateQuestionCounterLabel()
            self.gameEnd()

    def gameEnd(self):
        if self.time_limit == 0: #and not self.game_ended:
            self.started = False
            self.timer.stop()
            # self.game_ended = True
            # print(f"Game ended by timer? {self.game_ended}")
            if self.timer_radio.isChecked():
                self.displayIncorrectWords()
                self.resetGame()
            return None
        
        if self.current < self.queue.shape[0]: # if there are still questions left
            self.displayQuestion()
        else:
            if self.loop_radio.isChecked(): # loop mode
                self.startGame()
            elif self.timer_radio.isChecked():
                # self.game_ended = True
                self.started = False
                # print(f"Game ended by questions over? {self.game_ended}")
                # self.current -= 1
                self.timer.stop()
                self.displayIncorrectWords()
                
                self.resetGame()
                    
        return None

    def displayIncorrectWords(self):
        dlg = CustomDialog(self.queue.iloc[self.incorrect_words], self.queue.shape[0]-self.current)
        dlg.exec()

    def resetKanjiLabel(self):
        self.kanji_label.setText("--")

    def resetTimerLabel(self):
        self.timer_label.setText(None)
        self.timer_label

    def resetAnswerInput(self):
        # self.answer_input.setText(None)
        self.answer_input.setObjectName("kanjiSpellAnswerInput")

        style = self.answer_input.style()
        style.unpolish(self.answer_input)
        style.polish(self.answer_input)
        self.answer_input.update()

    def resetAnswerLabel(self):
        self.answer_label.setText(None)
        # self.answer_input.setStyleSheet("""
        #     min-height: 60px;
        #     min-width: 200px;
        #     font-family: 'Arial', sans-serif;
        #     background: rgba(247, 247, 247, 1);
        # """)

    def displayEnglish(self):
        if self.started:
            if self.display_en:
                self.english_label.setText(self.queue['en'].iloc[self.current])
                self.setFontSize(self.english_label, self.english_fontsize)
            else:
                self.english_label.setText(None)

            self.english_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def englishToggled(self, state):
        if state == 0:
            self.display_en = False
        else:
            self.display_en = True

        self.displayEnglish()
            
    def timerRadioToggled(self, state):
        # if state:
        self.spin_box.setEnabled(state)
        self.add_seconds_button.setEnabled(state)
        self.remove_seconds_button.setEnabled(state)
        if not state:
            self.spin_box.setStyleSheet("""background: #e8e8e5;""")
            self.add_seconds_button.setStyleSheet("""background: #e8e8e5;""")
            self.remove_seconds_button.setStyleSheet("""background: #e8e8e5;""")
        else:
            self.spin_box.setStyleSheet("""""")
            self.add_seconds_button.setStyleSheet("""""")
            self.remove_seconds_button.setStyleSheet("""""")

    def addSeconds(self):
        if self.timer_radio.isChecked():
            self.spin_box.setValue(self.spin_box.value()+10)

    def removeSeconds(self):
        if self.timer_radio.isChecked():
            value = self.spin_box.value()
            if value - 10 < 1:
                self.spin_box.setValue(1)
            else:
                self.spin_box.setValue(value+10)

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

        self.title = tools.getPageTitle(self.level, "Kanji Spell")
        self.title.setObjectName("pageTitle"+self.level)
        self.title_bar_layout.addWidget(self.title)

        self.container.addLayout(self.title_bar_layout)

        self.play_area = PlayArea(self.words, self.level)
        self.container.addWidget(self.play_area)

        self.setLayout(self.container)


