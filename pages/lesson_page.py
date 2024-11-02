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
    QDialog, QDialogButtonBox, QComboBox
)
from PyQt6.QtGui import QPixmap, QAction, QCursor
from PyQt6 import QtCore

styles = "assets\styles\styles.css"

class SelectGrammarDialog(QDialog):
    def __init__(self, level, user, parent=None, db=None):
        super().__init__(parent)
        self.db = db
        self.level = level
        self.user = user
        self.hide_completed = False
        self.grammars = None

        self.setWindowTitle("Select grammar")

        QBtn = (
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        self.combobox = QComboBox()
        self.populateComboBox()
        # self.combobox.addItems(['One', 'Two', 'Three', 'Four'])
        self.combobox.setEditable(True)
        self.combobox.currentTextChanged.connect(self.currentTextChanged)

        self.check_box = QCheckBox('Hide completed grammar points')
        self.check_box.stateChanged.connect(self.hideCompletedCheckBox)

        layout.addWidget(self.check_box)
        layout.addWidget(self.combobox)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def accept(self):
        print(self.combobox.currentText())
        print(self.combobox.currentIndex())
        print(self.grammars.iloc[self.combobox.currentIndex()])
        self.parent().setGrammarPoint(self.grammars.iloc[self.combobox.currentIndex()])
        self.close()

    def hideCompletedCheckBox(self, state):
        if state == 0:
            self.hide_completed = False
        else:
            self.hide_completed = True

        self.populateComboBox()


    def populateComboBox(self):
        print(self.hide_completed)
        df = self.db.get_user_grammars_all(self.level, self.user)
        if self.hide_completed: # Only display grammar points the user has not completed
            df = df[df["completed"] == False]
        
        print(df)
        for i in range(self.combobox.count()):
            self.combobox.removeItem(0)    
        self.combobox.addItems([f'{df["grammar_jp"].iloc[i]} | {df["grammar_en"].iloc[i]}' for i in range(df.shape[0])])

        self.grammars = df


    def currentTextChanged(self):
        pass


class GrammarPoint:
    def __init__(self, id, img, title, completed):
        self.id = id
        self.img = img
        self.title = title
        self.completed = completed

    def getGrammarInfo(self):
        return (self.id, self.img, self.title, self.completed)
    
    def setCompleted(self, state):
        self.completed = state

class GrammarList:
    def __init__(self):
        self.hist = []
        self.current = -1

    def add(self, id, img, title, completed):
        self.hist.append(GrammarPoint(id, img, title, completed))

    def insert(self, id, img, title, completed, idx):
        self.hist = self.hist[:idx] + [GrammarPoint(id, img, title, completed)] + self.hist[idx:]
        if idx <= self.current:
            self.setCurrent(self.current + 1)

    def insertNext(self, id, img, title, completed):
        if self.current == len(self.hist) - 1:
            self.add(id, img, title, completed)
        else:
            self.insert(id, img, title, completed, self.current+1)

    def setCompletedCurrent(self, state):
        if not self.getIsStart(): # Cannot complete the filler grammar point
            self.hist[self.current].setCompleted(state)

    def setCurrent(self, idx):
        if idx >= 0 and idx < len(self.hist):
            self.current = idx

    def getCurrent(self):
        if self.current >= 0:
            return self.hist[self.current].getGrammarInfo() + (self.current,) # Make 4-tuple
        else:
            return None
        
    def getIsEnd(self):
        if self.current == len(self.hist) - 1: # Return True if the current grammar is the last grammar in the list
            return True
        else: 
            return False

    def getIsStart(self):
        if self.current == 0:
            return True
        else:
            return False
        
    def loadNext(self):
        
        if not self.getIsEnd():
            
            self.setCurrent(self.current + 1)
            print(self.getCurrent())
            return self.getCurrent()
        else:
            return None

    def loadPrevious(self):
        if not self.getIsStart():
            self.current -= 1
            return self.getCurrent()
        else:
            return None
        
    def getLength(self):
        return len(self.hist)
    
    def getAtIndex(self, idx):
        return self.hist[idx].getGrammarInfo() + (idx,)


class LessonPage(QWidget):
    ### Grammar point information is currently stored as an image url which is HTML requested as needed. Image data is not stored in db.
    def __init__(self, level):
        super().__init__()
        self.user = 1 # Temporary user id - ADD LOGIN FUNCTIONALITY
        self.level = level
        self.grammar_list = GrammarList()
        self.randomise = False
        self.db = Database()
        self.grammar_list.add(-1, 'assets//images//white.png', '<Select a grammar or press Next Grammar>', False) # Add a blank image to be displayed until a button is pressed
        user_grammars = self.db.get_user_grammars_not_completed(self.level, self.user)
        for i in range(user_grammars.shape[0]):
            self.grammar_list.add(user_grammars['grammar_id'].iloc[i], user_grammars['image_url'].iloc[i], self.makeTitle(user_grammars['grammar_en'].iloc[i], user_grammars['grammar_jp'].iloc[i]), False)

        self.grammar_image = QLabel()

        


        self.grammar_title_container = QHBoxLayout()
        self.grammar_title = QLabel('')
        self.grammar_title.setMaximumWidth(600)
        font = self.grammar_title.font()
        font.setPointSize(30)
        self.grammar_title.setFont(font)
        self.grammar_title_container.addWidget(self.grammar_title)
        self.grammar_title_container.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.randomise_button = QPushButton('Randomise', self)
        self.randomise_button.clicked.connect(self.randomiseGrammar)
        self.randomise_button.setProperty("class", "lessonButton")
        self.randomise_button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

        self.select_grammar_button = QPushButton('Select Grammar', self)
        self.select_grammar_button.clicked.connect(self.selectGrammar)
        self.select_grammar_button.setProperty("class", "lessonButton")
        self.select_grammar_button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))


        self.set_complete_layout = QHBoxLayout()
        self.check_box = QCheckBox('Set grammar complete')
        self.check_box.setCheckState(Qt.CheckState.Checked)
        self.check_box.stateChanged.connect(self.completeBoxChecked)
        self.set_complete_layout.addWidget(self.check_box)

        self.previous_grammar_button = QPushButton('< Previous Grammar')
        self.previous_grammar_button.clicked.connect(self.previous)
        self.previous_grammar_button.setProperty("class", "lessonButton")
        self.previous_grammar_button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))  

        self.practice_button = QPushButton('Practice')  
        # self.practice_button.clicked.connect(self.displayPreviousGrammar)
        self.practice_button.setProperty("class", "lessonButton")
        self.practice_button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))  

        self.next_grammar_button = QPushButton('Next Grammar >')
        self.next_grammar_button.clicked.connect(self.next)
        self.next_grammar_button.setProperty("class", "lessonButton")
        self.next_grammar_button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.randomise_button, 0,0,1,1)
        self.grid_layout.addWidget(self.select_grammar_button, 0,4,1,1)
        self.grid_layout.addLayout(self.grammar_title_container, 0,1,1,3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(self.grammar_image, 1,1,2,3)
        self.grid_layout.addLayout(self.set_complete_layout, 4,2)
        self.grid_layout.addWidget(self.previous_grammar_button, 5,1,1,1)
        self.grid_layout.addWidget(self.next_grammar_button, 5,3,1,1)
        # self.grid_layout.setRowMinimumHeight(0,75)
        # self.grid_layout.setRowMinimumHeight(5,100)
        self.grid_layout.setColumnMinimumWidth(0,100)
        self.grid_layout.setColumnMinimumWidth(4,100)

        self.outer_container = QHBoxLayout()
        self.outer_container.setContentsMargins(50,50,50,50)
        self.outer_container.addLayout(self.grid_layout)

        with open(styles, 'r') as f:
            self.setStyleSheet(f.read())

        self.next() # Display the blank image
        # self.display(*self.grammar_list.getCurrent())
        
        self.setLayout(self.outer_container)

    def display(self, id, img, title, completed, idx):
        if not idx == 0:
            print(idx)
            print(img)
            response = requests.get(img, stream=True)
            with open('img.png', 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
            pixmap = QPixmap(r'img.png')
            self.check_box.show() # Display the check box for grammar completion
            self.check_box.setChecked(completed)
        else:
            pixmap = QPixmap(img)
            self.grammar_image.setPixmap(pixmap)
            self.check_box.hide()

        self.grammar_image.setPixmap(pixmap)
        self.grammar_title_label = title
        self.grammar_title.setText(self.grammar_title_label)

        if self.grammar_list.getIsEnd():
            self.next_grammar_button.setEnabled(False)
        else:
            self.next_grammar_button.setDisabled(False)

        if self.grammar_list.getIsStart():
            self.previous_grammar_button.setEnabled(False)
        else:
            self.previous_grammar_button.setDisabled(False)

        # self.check_box.setChecked(False)

    def next(self):
        next_grammar = self.grammar_list.loadNext()
        print(next_grammar)
        if not next_grammar is None:
            self.display(*next_grammar) # Send result tuple as unpacked tuple
            
    def previous(self):
        prev_grammar = self.grammar_list.loadPrevious()
        if not prev_grammar is None:
            self.display(*prev_grammar) # Send result tuple as unpacked tuple
            

    def completeBoxChecked(self, state):
        id = self.grammar_list.getCurrent()[0]

        if state == 0:
            state = False
        else:
            state = True

        self.grammar_list.setCompletedCurrent(state)
        self.db.set_user_grammar_status(self.user, id, state)
        

    def selectGrammar(self):
        self.select_dialog = SelectGrammarDialog(level=self.level, user=self.user, parent=self, db=self.db)
        self.select_dialog.exec()

    def randomiseGrammar(self):
        idx = random.randint(1, self.grammar_list.getLength() - 1)
        self.grammar_list.setCurrent(idx)
        self.display(*self.grammar_list.getCurrent())

    def setGrammarPoint(self, info):

        for i in range(self.grammar_list.getLength()):
            if self.grammar_list.getAtIndex(i)[0] == info["grammar_id"]: # If grammar point with chosen id is already in the list, set it as current grammar
                self.grammar_list.setCurrent(i)
                self.display(*self.grammar_list.getCurrent())
                return None

        # grammar_info = self.db.get_grammar_info(id)
        self.grammar_list.insertNext(info["grammar_id"], info["image_url"], self.makeTitle(info["grammar_en"],info["grammar_jp"]), info["completed"])
        self.next()        

    def makeTitle(self, en, jp):
        return jp # + ' - ' + en