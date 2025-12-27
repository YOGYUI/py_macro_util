from PySide6.QtWidgets import (QWidget,
                               QTableWidget, QTableWidgetItem, QHeaderView)


class TaskListTableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._table = QTableWidget()
        self.initControl()
        self.initLayout()

    def initLayout(self):
        pass

    def initControl(self):
        pass
