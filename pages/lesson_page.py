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
    QAbstractButton, QListWidgetItem
)
from PyQt6.QtGui import QPixmap, QAction, QCursor, QPainter
from PyQt6 import QtCore
from assets.tools import Tools
tools = Tools()

styles = "assets\styles\styles.css"

class Example():
    def __init__(self, jp, en):
        self.jp = jp
        self.en = en
        self.hide_text_jp = '~'*(len(self.jp)//2+1)
        self.hide_text_en = '~'*(len(self.en)//2+1)
        self.display_text_jp = self.jp
        self.display_text_en = self.en
        
    def getJp(self):
        return self.display_text_jp
    
    def getEn(self):
        return self.display_text_en

    def hideJp(self):
        self.display_text_jp = self.hide_text_jp
    
    def hideEn(self):
        self.display_text_en = self.hide_text_en
    
    def showJp(self):
        self.display_text_jp = self.jp

    def showEn(self):
        self.display_text_en = self.en

class ExamplesField(QWidget):
    def __init__(self):
        super().__init__()
        self.examples = None
        self.jp_hidden = False
        self.en_hidden = False
        
        self.scroll = QScrollArea()
        self.scroll.setProperty("class", "scrollArea")
        self.widget = QWidget()
        self.vbox = QVBoxLayout()  

        self.widget.setLayout(self.vbox)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.scroll)
        self.layout.setProperty("class", "scrollArea")
        self.setLayout(self.layout)

        with open(styles, "r") as f:
            self.setStyleSheet(f.read())

    def getJpHidden(self):
        return self.jp_hidden
    
    def getEnHidden(self):
        return self.en_hidden

    def setExamples(self, examples):
        self.examples = [Example(examples['example_jp'].iloc[i], examples['example_en'].iloc[i]) for i in range(examples.shape[0])]

    def update(self):
        if not self.examples is None:
            for i in reversed(range(self.vbox.count())): 
                self.vbox.itemAt(i).widget().setParent(None)

            if self.jp_hidden:
                self.setJpHiddenText()
            
            if self.en_hidden:
                self.setEnHiddenText()

            for i in range(len(self.examples)):
                jp = QLabel(self.examples[i].getJp(), alignment=Qt.AlignmentFlag.AlignCenter)
                jp.setWordWrap(True)
                # set font of japanese text
                font = jp.font()
                font.setPointSize(14)
                jp.setFont(font)
                self.vbox.addWidget(jp)
                en = QLabel(self.examples[i].getEn(), alignment=Qt.AlignmentFlag.AlignCenter)
                en.setWordWrap(True)
                # set font of English text
                font = en.font()
                font.setPointSize(14)
                en.setFont(font)
                self.vbox.addWidget(en)
                blank = QLabel()
                self.vbox.addWidget(blank)      


    def setJpHiddenText(self):
        for i in range(len(self.examples)):
            self.examples[i].hideJp()

    def hideJp(self):
        if not self.examples is None:
            self.jp_hidden = True
            self.setJpHiddenText()
            self.update()

    def setEnHiddenText(self):
        for i in range(len(self.examples)):
            self.examples[i].hideEn()

    def hideEn(self):
        if not self.examples is None:
            self.en_hidden = True
            self.setEnHiddenText()
            self.update()

    def showJp(self):
        if not self.examples is None:
            self.jp_hidden = False
            for i in range(len(self.examples)):
                self.examples[i].showJp()

            self.update()

    def showEn(self):
        if not self.examples is None:
            self.en_hidden = False
            for i in range(len(self.examples)):
                self.examples[i].showEn()

            self.update()

class QCustomListWidget(QWidget):
    def __init__ (self, idx, jp, en, complete = False, parent = None):
        super(QCustomListWidget, self).__init__(parent)
        self.text_vbox = QVBoxLayout()

        self.jp_text = QLabel(f'{idx}. {jp}')
        self.jp_text.setObjectName("selectWordFieldJp")
        self.en_text = QLabel(en)
        self.en_text.setObjectName("selectWordFieldEn")

        self.text_vbox.addWidget(self.jp_text)
        self.text_vbox.addWidget(self.en_text)
        self.text_vbox.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.complete_style = 'color: rgb(0, 0, 0);'
        self.incomplete_style = 'color: rgb(255, 60, 0);'

        self.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

        self.setStyle(complete)

        self.setLayout(self.text_vbox)

    def setStyle(self, complete):
        if complete:
            self.jp_text.setStyleSheet(self.complete_style)
            self.en_text.setStyleSheet(self.complete_style)
        else:
            self.jp_text.setStyleSheet(self.incomplete_style)
            self.en_text.setStyleSheet(self.incomplete_style)


class SelectGrammarField(QWidget):
    def __init__(self, level, user, parent=None, db=None, grammars=None):
        super().__init__(parent)
        self.db = db
        self.level = level
        self.user = user
        self.grammars = grammars

        self.outer_container = QVBoxLayout()

        self.widget_layout = QVBoxLayout()

        widget = QWidget()
        widget.setObjectName("selectGrammarWidget")

        self.title = QLabel('Grammar List')
        self.title.setObjectName("selectWordFieldTitle")

        self.widget_layout.addWidget(self.title)

        self.filter_buttons_layout = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("selectGrammarSearchBar")
        self.search_bar.textChanged.connect(self.filterList)

        self.random_btn = QPushButton('Randomise')
        # self.random_btn.setMaximumWidth(100)
        self.random_btn.setObjectName("randomiseButton")
        self.random_btn.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.random_btn.clicked.connect(self.randomBtnPressed)

        self.filter_buttons_layout.addWidget(self.search_bar)
        self.filter_buttons_layout.addWidget(self.random_btn)

        self.widget_layout.addLayout(self.filter_buttons_layout)

        # self.outer_container.addWidget(self.random_btn)

        self.list_widget = QListWidget()
        self.filterList()
        # self.list_items = [QCustomListWidget(i+1, self.grammars['jp'].iloc[i], self.grammars['en'].iloc[i], self.grammars['completed'].iloc[i]) for i in range(self.grammars.shape[0])]
        # for item in self.list_items:
        #     my_list_widget = QListWidgetItem(self.list_widget)
        #     # Set size hint
        #     my_list_widget.setSizeHint(item.sizeHint())
        #     # Add QListWidgetItem into QListWidget
        #     self.list_widget.addItem(my_list_widget)
        #     self.list_widget.setItemWidget(my_list_widget, item)
        # self.list_widget.addItems([f"{grammars['jp'].iloc[i]} | {grammars['en'].iloc[i]}" for i in range(grammars.shape[0])])
        self.list_widget.currentRowChanged.connect(self.rowChanged)

        self.widget_layout.addWidget(self.list_widget)

        widget.setLayout(self.widget_layout)
        self.outer_container.addWidget(widget)

        self.setLayout(self.outer_container)

    def filterList(self, text=""):
        ## 
        # TODO: Speed this up by
        ##

        self.list_widget.clear()
        self.list_items = []
        for i in range(self.grammars.shape[0]):
            if text in self.grammars['jp'].iloc[i] or text in self.grammars['en'].iloc[i]:
                self.list_items.append(QCustomListWidget(i+1, self.grammars['jp'].iloc[i], self.grammars['en'].iloc[i], self.grammars['completed'].iloc[i]))

        # print(self.list_items[0].jp_text)
        for item in self.list_items:
            my_list_widget = QListWidgetItem(self.list_widget)
            # Set size hint
            my_list_widget.setSizeHint(item.sizeHint())
            # Add QListWidgetItem into QListWidget
            self.list_widget.addItem(my_list_widget)
            self.list_widget.setItemWidget(my_list_widget, item)


    def updateItemCompletion(self, idx, state):
        self.list_items[idx].setStyle(state)

    def randomBtnPressed(self):
        self.parent().randomBtnPressed()

    def rowChanged(self, idx):
        self.parent().grammarSelected(idx)

    def scrollListView(self, idx):
        self.list_widget.scrollToItem(self.list_widget.item(idx))

class ArrowButton(QAbstractButton):
    def __init__(self, pixmap, dir, parent=None):
        super(ArrowButton, self).__init__(parent)
        self.dir = dir
        self.pixmap = pixmap.scaled(30,50, aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.clicked.connect(self.buttonPressed)
        self.setMaximumHeight(50)
        self.setMaximumWidth(30)

        self.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()

    def buttonPressed(self):
        if self.dir == 'left':
            self.parent().leftButtonPressed()
        elif self.dir == 'right':
            self.parent().rightButtonPressed()

class LessonPage(QWidget):
    ### Grammar point information is currently stored as an image url which is HTML requested as needed. Image data is not stored in db.
    def __init__(self, level):
        super().__init__()
        self.user = 1 # Temporary user id - ADD LOGIN FUNCTIONALITY
        self.level = level.upper()

        self.db = Database()
        self.grammars = self.db.get_user_grammars_all(self.level, self.user)
        self.num_grammars = self.grammars.shape[0]
        self.grammars.columns = ['id', 'en', 'jp', 'url', 'level_id', 'completed']
        self.selected = 0 # Index of currently selected grammar

        self.title = tools.getPageTitle(self.level, "Grammar Lesson")
        self.title.setObjectName("pageTitle"+self.level)

        self.grammar_image = QLabel()
        self.grammar_title = QLabel(self.makeTitle(self.grammars['en'].iloc[0], self.grammars['jp'].iloc[0]))
        self.grammar_title.setObjectName("grammarTitle")

        self.title_container = QVBoxLayout()
        self.title_container.addWidget(self.title)
        # self.title_container.addWidget(self.grammar_title)
        self.title_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.select_grammar_field = SelectGrammarField(self.level, self.user, self, self.db, self.grammars)
        self.select_grammar_field.setMaximumWidth(400)
        self.select_grammar_field.setContentsMargins(50,0,0,0)

        self.lesson_container = QHBoxLayout()

        self.grammar_info_container = QVBoxLayout()

        ## Contains the grammar image and arrows for changing current grammar
        self.grammar_image_container = QHBoxLayout()

        pixmap = QPixmap(r'assets//images//arrow_left.png')
        self.left_arrow = ArrowButton(pixmap, 'left')
        pixmap = QPixmap(r'assets//images//arrow_right.png')
        self.right_arrow = ArrowButton(pixmap, 'right')

        self.grammar_image_container.addWidget(self.left_arrow)
        self.grammar_image_container.addWidget(self.grammar_image)
        self.grammar_image_container.addWidget(self.right_arrow)

        self.grammar_image_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grammar_info_container.addLayout(self.grammar_image_container)

        self.examples_container = QVBoxLayout()

        self.examples_btn_container = QHBoxLayout()
        self.hide_en_btn = QPushButton('Hide EN')
        self.hide_en_btn.setMaximumWidth(100)
        self.hide_en_btn.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.hide_en_btn.setProperty("class", "button")
        self.hide_en_btn.clicked.connect(self.enToggleBtnPressed)
        self.hide_jp_btn = QPushButton('Hide JP')
        self.hide_jp_btn.setMaximumWidth(100)
        self.hide_jp_btn.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.hide_jp_btn.setProperty("class", "button")
        self.hide_jp_btn.clicked.connect(self.jpToggleBtnPressed)

        self.check_box = QCheckBox('Set grammar completed')
        self.check_box.stateChanged.connect(self.checked)

        self.examples_btn_container.addWidget(self.check_box)
        self.examples_btn_container.addWidget(self.hide_en_btn)
        self.examples_btn_container.addWidget(self.hide_jp_btn)   
        self.examples_btn_container.setAlignment(Qt.AlignmentFlag.AlignRight) 

        self.examples = ExamplesField()

        self.examples_container.addLayout(self.examples_btn_container)
        self.examples_container.addWidget(self.examples)

        self.grammar_info_container.addLayout(self.examples_container)

        self.lesson_container.addLayout(self.grammar_info_container)
        self.lesson_container.addWidget(self.select_grammar_field)
        
        self.display()

        self.outer_container = QVBoxLayout()
        self.outer_container.addLayout(self.title_container)
        self.outer_container.addLayout(self.lesson_container)

        # with open(styles, 'r') as f:
        #     self.setStyleSheet(f.read())
        
        self.setLayout(self.outer_container)

    def display(self):
        # updates UI to display the grammar at the index of `self.selected` in the self.grammars dataframe
        response = requests.get(self.grammars['url'].iloc[self.selected], stream=True)
        with open('img.png', 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        pixmap = QPixmap(r'img.png')
        # pixmap = pixmap.scaledToHeight(pixmap.height()*0.9)

        examples_info = self.db.get_examples(self.grammars['id'].iloc[self.selected])
        print(self.grammars['id'].iloc[self.selected])
        print(examples_info)
        self.examples.setExamples(examples_info)
        self.examples.update()

        self.grammar_image.setPixmap(pixmap)
        self.grammar_title.setText(self.makeTitle(self.grammars['en'].iloc[self.selected], self.grammars['jp'].iloc[self.selected]))

        self.select_grammar_field.scrollListView(self.selected)

        if self.grammars['completed'].iloc[self.selected]:
            self.check_box.setCheckState(Qt.CheckState.Checked)
        else:
            self.check_box.setCheckState(Qt.CheckState.Unchecked)

    def leftButtonPressed(self):
        if self.selected >= 1:
            self.grammarSelected(self.selected - 1)
        
    def rightButtonPressed(self):
        if self.selected < self.num_grammars - 1:
            self.grammarSelected(self.selected + 1)

    def grammarSelected(self, idx):
        self.selected = idx
        self.display()

    def jpToggleBtnPressed(self):
        if self.examples.getJpHidden(): # If the Japanese text is currently hidden
            self.hide_jp_btn.setText('Hide JP')
            self.examples.showJp()
        else: # If the Japanese text is currently being shown
            self.hide_jp_btn.setText('Show JP')
            self.examples.hideJp()

    def enToggleBtnPressed(self):
        if self.examples.getEnHidden(): # If the English text is currently hidden
            self.hide_en_btn.setText('Hide En')
            self.examples.showEn()
        else: # If the English text is currently being shown
            self.hide_en_btn.setText('Show En')
            self.examples.hideEn()

    def randomBtnPressed(self):
        # choose a random grammar to display
        rand = random.randint(1,self.num_grammars-1)
        print(rand)
        self.selected = rand
        self.display()

    def hideEn(self):
        self.examples.hideEn()

    def checked(self, state):
        if state == 2:
            state = True
        elif state == 0:
            state = False

        self.db.set_user_grammar_status(self.user, self.grammars['id'].iloc[self.selected], state) # update completion status in database
        self.grammars['completed'].iloc[self.selected] = state # locally update the completion status
        self.select_grammar_field.updateItemCompletion(self.selected, state)

    def makeTitle(self, en, jp):
        return f'{self.selected+1}. {jp}' # + ' - ' + en