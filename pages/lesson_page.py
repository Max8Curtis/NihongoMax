from database import Database
from bs4 import BeautifulSoup
import requests
import shutil

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, 
    QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QToolBar,
    QStatusBar, QStackedLayout, QGridLayout, QCheckBox
)
from PyQt6.QtGui import QPixmap, QAction, QIcon


class LessonPage(QWidget):
    ### Grammar point information is currently stored as an image url which is HTML requested as needed. Image data is not stored in db.
    def __init__(self, level):
        super().__init__()
        self.user = 1 # Temporary user id - ADD LOGIN FUNCTIONALITY
        self.level = level
        self.grammar_point = None # Id of chosen grammar point
        self.randomise = False
        self.db = Database()

        self.grammar_image = QLabel(self)
        # pixmap = QPixmap(r"assets//images//zeimusu-kanji-e-3120189007-resized.png")
        pixmap = QPixmap(r"assets//images//white.png")
        self.grammar_image.setPixmap(pixmap)
        self.grammar_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.randomise_button = QPushButton('Randomise', self)
        self.randomise_button.clicked.connect(self.randomiseGrammar)
        self.select_grammar_button = QPushButton('Select Grammar', self)
        self.select_grammar_button.clicked.connect(self.selectGrammar)

        self.set_complete_layout = QHBoxLayout()
        self.check_box = QCheckBox()
        self.check_box.setCheckState(Qt.CheckState.Checked)
        self.check_box_label = QLabel('Set grammar complete')
        self.check_box.stateChanged.connect(self.completeBoxChecked)
        self.set_complete_layout.addWidget(self.check_box)
        self.set_complete_layout.addWidget(self.check_box_label)

        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.randomise_button, 0,0,1,1)
        self.grid_layout.addWidget(self.select_grammar_button, 0,4,1,1)
        self.grid_layout.addWidget(self.grammar_image, 1,1,2,3)
        self.grid_layout.addLayout(self.set_complete_layout, 4, 2)



        self.grammar_point = 1
        self.displayGrammarInfo()
        
        self.setLayout(self.grid_layout)

    def completeBoxChecked(self, state):
        # state = self.check_box.isChecked()
        if state == 0:
            state = False
        else:
            state = True
        self.db.set_user_grammar_status(self.user, self.grammar_point, state)

    def selectGrammar(self):
        pass

    def randomiseGrammar(self):
        pass
        grammar_info = self.db.select_random_grammar(self.user, self.level)
        self.grammar_point = grammar_info[0]
        self.displayGrammarInfo()
        self.check_box.setChecked(False)


    def displayGrammarInfo(self):
        if self.grammar_point is not None:
            image_url = self.db.get_grammar_info(self.grammar_point)
            if image_url is None:
                return None

            response = requests.get(image_url, stream=True)
            with open('img.png', 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
            print("here")
            pixmap = QPixmap(r"img.png")
            self.grammar_image.setPixmap(pixmap)




    