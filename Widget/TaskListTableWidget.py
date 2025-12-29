import os
import sys

from PyQt5.QtWidgets import QSizePolicy
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QWidget, QPushButton,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QVBoxLayout, QHBoxLayout, QSizePolicy)
CUR_PATH = os.path.dirname(os.path.abspath(__file__))  # {PROJ}/Task
PROJ_PATH = os.path.dirname(CUR_PATH)
sys.path.extend([CUR_PATH, PROJ_PATH])
sys.path = list(set(sys.path))
from AppCore import AppCore


class TaskListTableWidget(QWidget):
    _core: AppCore = None

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._btn_add_task = QPushButton()
        self._btn_remove_task = QPushButton()
        self._btn_clear_task = QPushButton()
        self._btn_move_task_up = QPushButton()
        self._btn_move_task_down = QPushButton()
        self._table = QTableWidget()
        self.initControl()
        self.initLayout()

    def initLayout(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(4)

        subwgt = QWidget()
        subwgt.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        hbox = QHBoxLayout(subwgt)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(4)
        hbox.addWidget(self._btn_add_task)
        hbox.addWidget(self._btn_remove_task)
        hbox.addWidget(self._btn_move_task_up)
        hbox.addWidget(self._btn_move_task_down)
        hbox.addWidget(self._btn_clear_task)

        hbox.addWidget(QWidget())
        vbox.addWidget(subwgt)
        vbox.addWidget(self._table)

    def initControl(self):
        self._btn_add_task.setIcon(QIcon("./Resource/Icon/plus.png"))

    def setCore(self, core: AppCore):
        self._core = core
        self.drawTaskList()

    def drawTaskList(self):
        pass
