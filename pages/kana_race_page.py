from database import Database
from bs4 import BeautifulSoup
import requests
import shutil
import random
from romaji.convert import Convert
import time
import pykakasi
import itertools


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
    def __init__(self, idx, jp, en, selected, parent = None):
        super(QCustomListWidget, self).__init__(parent)

    def clicked(self):
        pass


class SelectTextField(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.types = self.db.get_text_types()
        # self.types = types
        self.texts = self.db.get_texts_all()
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
        self.type_combobox.currentIndexChanged.connect(self.updateTypeSelection)

        self.random_btn = QPushButton('Randomise')
        # self.random_btn.setMaximumWidth(100)
        self.random_btn.setObjectName("randomiseButton")
        self.random_btn.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
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

    def filterListItems(self, filter_ex = None):
        ## TODO:
        #  Add sophisticated searching and order list items by similarity to the search text
        ##
        if filter_ex is None:
            self.list_items = [QCustomListWidget(idx=self.texts['id'].iloc[i], jp=self.texts['title'].iloc[i], en=f"{self.texts['author'].iloc[i]} - Length: {self.texts['length'].iloc[i]}", selected=False) for i in range(self.texts.shape[0]) if self.texts['type_id'].iloc[i] == self.type_labels['id'][self.selected_type_idx]]
        else:
            filter_ex = filter_ex.lower()
            self.list_items = [QCustomListWidget(idx=self.texts['id'].iloc[i], jp=self.texts['title'].iloc[i], en=f"{self.texts['author'].iloc[i]} - Length: {self.texts['length'].iloc[i]}", selected=False) for i in range(self.texts.shape[0]) if self.texts['type_id'].iloc[i] == self.type_labels['id'][self.selected_type_idx] and (filter_ex in self.texts['title'].iloc[i].lower() or filter_ex in self.texts['author'].iloc[i].lower())]


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
        type_tuples = [(self.types['type_id'].iloc[x], self.types['type'].iloc[x]) for x in range(self.types.shape[0])]
        type_labels = {'id': [], 'label': []}
        for i in range(len(type_tuples) + 1):
            for subset in itertools.combinations(type_tuples, i):
                if len(subset) > 0:
                # print(subset)
                    type_labels['id'].append([subset[i][0] for i in range(len(subset))])
                    label = ''.join([subset[i][1]+"+" for i in range(len(subset))])
                    type_labels['label'].append(label[:len(label)-1])

        return type_labels

    def randomBtnPressed(self):
        pass

    def rowChanged(self, idx):
        pass

class PlayArea(QWidget):
    def __init__(self, level, db):
        super().__init__()
        self.level = level
        self.db = db

        self.container = QHBoxLayout()

        self.select_text_field = SelectTextField(self.db)
        
        self.container.addWidget(self.select_text_field)

        self.setLayout(self.container)

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

        self.play_area = PlayArea(self.level, self.db)
        self.container.addWidget(self.play_area)

        self.setLayout(self.container)


