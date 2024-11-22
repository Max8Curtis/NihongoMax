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

class WordMatchPage(QWidget):
    def __init__(self):
        super().__init__()
        