from PySide6.QtWidgets import (QWidget, QMainWindow)


class AboutWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.initControl()
        self.initLayout()

    def initLayout(self):
        pass

    def initControl(self):
        pass


class AboutWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._widget = AboutWidget(self)
        self.initControl()
        self.initLayout()

    def initLayout(self):
        self.setCentralWidget(self._widget)

    def initControl(self):
        pass
