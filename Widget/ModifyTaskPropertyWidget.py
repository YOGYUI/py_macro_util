import os
import sys
from PySide6.QtWidgets import (QWidget, QTreeWidget, QTreeWidgetItem)
CUR_PATH = os.path.dirname(os.path.abspath(__file__))  # {PROJ}/Widget
PROJ_PATH = os.path.dirname(CUR_PATH)
sys.path.extend([CUR_PATH, PROJ_PATH])
sys.path = list(set(sys.path))
from AppCore import AppCore
from Task import *


class ModifyTaskPropertyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def initLayout(self):
        pass

    def initControl(self):
        pass

    def updateControl(self):
        pass