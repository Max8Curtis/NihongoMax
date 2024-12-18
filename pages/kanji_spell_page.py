from database import Database
from bs4 import BeautifulSoup
import requests
import shutil
import random

from PyQt6.QtCore import QSize, Qt
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
from assets.widgets import SelectWordField
from assets.tools import Tools
tools = Tools()

styles = "assets\styles\styles.css"

class PlayArea(QWidget):
    def __init__(self):
        super().__init__()

        self.options_container = QHBoxLayout()
        self.options_grid = QGridLayout()

        self.options_label = QLabel('Options:')
        self.setFontSize(self.options_label, 20)
        self.options_container.addWidget(self.options_label)

        self.spin_box = QSpinBox(self)
        self.spin_box.setRange(0, 600)  # Set the range of values
        self.spin_box.setValue(1)
        self.loop_radio = QRadioButton('Loop', self)
        self.options_grid.addWidget(self.loop_radio, 0, 0)   
        self.timer_radio = QRadioButton('Timer (seconds)', self)
        self.timer_radio.toggled.connect(self.timerRadioToggled)
        self.options_grid.addWidget(self.timer_radio, 1, 0)   
        self.options_grid.addWidget(self.spin_box, 1, 1)

        self.options_container.addLayout(self.options_grid)

        self.setLayout(self.options_container) 
    
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

        self.play_area = PlayArea()
        self.container.addWidget(self.play_area)

        self.setLayout(self.container)


