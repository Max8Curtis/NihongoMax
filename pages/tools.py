from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, 
    QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QToolBar,
    QStatusBar
)
from PyQt6.QtGui import QPixmap, QAction, QCursor
from PyQt6 import QtCore

class LessonPage(QWidget):
    def __init__(self):
        super().__init__()

        