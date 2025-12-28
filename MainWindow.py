from PySide6.QtWidgets import QMainWindow
from Widget import *
from AppCore import AppCore


class MainWindow(QMainWindow):
    _core: AppCore = None

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MACRO")
        self.initControl()
        self.initLayout()

    def initLayout(self):
        pass

    def initControl(self):
        pass
