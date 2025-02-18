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
import pandas as pd


class Time:
    def __init__(self):
        pass

    def secondsToMinutesSeconds(self, s):
        try:
            mins = int(s // 60)
            secs = int(s % 60)
            return f"{str(mins).zfill(2)}:{str(secs).zfill(2)}"
        except:
            return None

    def minutesSecondsToSeconds(self, time):
        # t comes in the form '--:--'
        # try:
        suma = sum(map(lambda x: int(x[0])*(60**int(x[1])), [(time.split(':')[y], len(
            time.split(':'))-1-y) for y in range(len(time.split(':'))-1, -1, -1)]))

        print(suma)
        return suma
        # except:
        #     return None

    def formatMinutesSeconds(self, m, s):
        # print(type(m))
        # print(s)
        if pd.isna(m) or pd.isna(s):
            return '--:--'
        return f"{'{:02d}'.format(m)}:{'{:02d}'.format(s)}"


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
        # self.setFontSize(title, 24)
        # title.setStyleSheet(self.getPageTitleStyling(level))
        return title
