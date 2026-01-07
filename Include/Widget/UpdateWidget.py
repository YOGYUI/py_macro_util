from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QWidget, QMainWindow)


class UpdateWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.initControl()
        self.initLayout()

    def initLayout(self):
        pass

    def initControl(self):
        pass


class UpdateWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._widget = UpdateWidget(self)
        self.initControl()
        self.initLayout()

    def initLayout(self):
        self.setCentralWidget(self._widget)

    def initControl(self):
        pass
