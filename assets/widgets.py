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

styles = "assets\styles\styles.css"


class StartButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.outer_container = QHBoxLayout()
        self.start_button = QPushButton()
        self.start_button.setObjectName("startButton")
        # self.start_button.setMinimumHeight(50)
        # self.start_button.setMinimumWidth(100)
        self.start_button_layout = QHBoxLayout()
        self.start_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.start_label = QLabel('Start')
        # self.setFontSize(self.start_label, 18)
        self.start_button_layout.addWidget(self.start_label)
        self.start_button.setCursor(
            QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        # self.start_button.setProperty("class", "button")
        self.start_button.setLayout(self.start_button_layout)
        self.start_button.clicked.connect(self.startBtnPressed)

        with open(styles, "r") as f:
            self.setStyleSheet(f.read())

        self.outer_container.addWidget(self.start_button)
        self.setLayout(self.outer_container)

    def startBtnPressed(self):
        self.parent().startBtnPressed()

    def setFontSize(self, obj: QWidget, size: int):
        font = obj.font()
        font.setPointSize(size)
        obj.setFont(font)
        return obj


class QCustomListWidget(QWidget):
    def __init__(self, idx, jp, en, selected, parent=None):
        super(QCustomListWidget, self).__init__(parent)
        self.idx = idx
        self.text_vbox = QVBoxLayout()
        self.selected = selected

        self.jp_text = QLabel(f'{jp}')
        self.jp_text.setObjectName("selectWordFieldJp")
        self.en_text = QLabel(en)
        self.en_text.setObjectName("selectWordFieldEn")

        self.text_vbox.addWidget(self.jp_text)
        self.text_vbox.addWidget(self.en_text)
        self.text_vbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # self.clicked.connect(self.updateStyle)

        self.selected_style = 'color: rgb(3, 133, 3);'
        self.unselected_style = 'color: rgb(0, 0, 0);'

        self.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

        self.setLayout(self.text_vbox)

    def updateStyle(self):
        if self.selected:  # If item is selected when it is pressed, it should now be displayed as unselected
            # self.jp_text.setStyleSheet(self.selected_style)
            # self.en_text.setStyleSheet(self.selected_style)
            # pass
            self.jp_text.setObjectName("selected")
            self.en_text.setObjectName("selected")
        else:
            # self.jp_text.setStyleSheet(self.unselected_style)
            # self.en_text.setStyleSheet(self.unselected_style)
            self.jp_text.setObjectName("selectWordFieldJp")
            self.en_text.setObjectName("selectWordFieldEn")

        style = self.jp_text.style()
        style.unpolish(self.jp_text)
        style.polish(self.jp_text)
        self.jp_text.update()

        style = self.en_text.style()
        style.unpolish(self.en_text)
        style.polish(self.en_text)
        self.en_text.update()

        # self.jp_text.update()
        # self.en_text.update()

    def clicked(self):
        self.selected = not self.selected
        self.updateStyle()

    def setSelected(self, s):
        if type(s) == bool:
            self.selected = s
            self.updateStyle()

    def getSelected(self):
        return self.selected

    def getIdx(self):
        return self.idx


class SelectWordField(QWidget):
    def __init__(self, parent=None, words=None):
        super().__init__(parent)
        self.words = words

        self.outer_container = QVBoxLayout()

        self.title = QLabel('Word List')

        self.outer_container.addWidget(self.title)

        self.select_all_btn = QPushButton('Select all')
        # self.select_all_btn.setMaximumWidth(100)
        # self.select_all_btn.setProperty("class", "button")
        self.select_all_btn.setObjectName("selectAllButton")
        self.select_all_btn.setCursor(
            QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.select_all_btn.clicked.connect(self.selectAllBtnPressed)
        self.select_all_pressed = False

        self.outer_container.addWidget(self.select_all_btn)

        self.list_widget = QListWidget()
        self.list_widget.setMinimumWidth(300)
        self.list_items = [QCustomListWidget(idx=words['id'].iloc[i], jp=words['ka'].iloc[i],
                                             en=words['en'].iloc[i], selected=False) for i in range(self.words.shape[0])]
        for item in self.list_items:
            item.setObjectName("selectWordListWidget")
            my_list_widget = QListWidgetItem(self.list_widget)
            # Set size hint
            my_list_widget.setSizeHint(item.sizeHint())
            # Add QListWidgetItem into QListWidget
            self.list_widget.addItem(my_list_widget)
            self.list_widget.setItemWidget(my_list_widget, item)

        self.list_widget.itemClicked.connect(self.updateItem)

        self.outer_container.addWidget(self.list_widget)
        self.outer_container.setProperty("class", "select")

        self.setLayout(self.outer_container)

    def getChosenWords(self):
        word_ids = [word.getIdx()
                    for word in self.list_items if word.getSelected()]
        return word_ids
        # return self.words.iloc[np.where(self.words['id'] in word_ids)]

    def updateItem(self):
        print(f'{self.list_widget.currentRow()} clicked!')
        self.list_items[self.list_widget.currentRow()].clicked()
        # self.parent().setSelected(self.list_items[self.list_widget.currentRow()].getIdx(), self.list_items[self.list_widget.currentRow()].getSelected())

    def selectAllBtnPressed(self):
        self.select_all_pressed = not self.select_all_pressed
        if self.select_all_pressed:
            self.select_all_btn.setText('Deselect all')
        else:
            self.select_all_btn.setText('Select all')

        for i in range(len(self.list_items)):
            self.list_items[i].setSelected(self.select_all_pressed)
            # self.parent().setSelected(self.list_items[i].getIdx(), self.select_all_pressed)
