from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, 
    QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QToolBar,
    QStatusBar, QStackedLayout, QGridLayout, QCheckBox, QMenu,
    QDialog, QDialogButtonBox, QComboBox, QListWidget, QListWidgetItem
)
from PyQt6.QtGui import QPixmap, QAction, QCursor
from PyQt6 import QtCore
from assets.styles.colors import Color

class Tools:
    def __init__(self):
        self.colors = Color()

    def setFontSize(self, obj: QWidget, size: int):
        font = obj.font()
        font.setPointSize(size)
        obj.setFont(font)
        return obj
    
    def getPageTitleStyling(self, level):
        return f"""
        color: #{self.colors.get_level_color(level)};
        font-family: Titillium;
        """
    
    def getPageTitle(self, level, text):
        title = QLabel(f'{level.upper()} {text}')
        self.setFontSize(title, 24)
        title.setStyleSheet(self.getPageTitleStyling(level))
        return title


        