import os
from typing import Union
from enum import IntEnum, unique
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction, QMouseEvent
from PySide6.QtWidgets import (QTreeWidgetItem, QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit, QPushButton)


def ensure_path_exist(path: str):
    targetpath = os.path.abspath(path)
    if not os.path.isdir(targetpath):
        if os.name == 'nt':
            pathsplit = targetpath.split('\\')
            ptemp = str(pathsplit[0]) + '\\'
        else:
            pathsplit = targetpath.split('/')
            ptemp = str(pathsplit[0]) + '/'
        for i in range(len(pathsplit) - 1):
            p = pathsplit[i + 1]
            ptemp = os.path.join(ptemp, p)
            ptemp = os.path.abspath(ptemp)
            if not os.path.isdir(ptemp):
                os.mkdir(ptemp)


class MyQAction(QAction):
    _level: int = 0

    def __init__(self, parent, level: int = 0):
        super().__init__(parent=parent)
        self._level = level

    @property
    def level(self):
        return self._level


def make_qaction(**kwargs):
    parent = None
    text = None
    iconPath = None
    triggered = None
    checkable = False
    checked = False
    level = 0

    if 'parent' in kwargs.keys():
        parent = kwargs['parent']
    if 'text' in kwargs.keys():
        text = kwargs['text']
    if 'iconPath' in kwargs.keys():
        iconPath = kwargs['iconPath']
    if 'triggered' in kwargs.keys():
        triggered = kwargs['triggered']
    if 'checkable' in kwargs.keys():
        checkable = kwargs['checkable']
    if 'checked' in kwargs.keys():
        checked = kwargs['checked']
    if 'level' in kwargs.keys():
        level = kwargs['level']

    action = MyQAction(parent, level)
    action.setText(text)
    action.setIcon(QIcon(iconPath))
    if triggered is not None:
        action.triggered.connect(triggered)
    action.setCheckable(checkable)
    action.setChecked(checked)

    return action


class CustomLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def mouseDoubleClickEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.MouseButton.LeftButton:
            self.selectAll()
            a0.accept()


class CustomDoubleSpinBox(QDoubleSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        customLineEdit = CustomLineEdit(self)
        self.setLineEdit(customLineEdit)


@unique
class PropType(IntEnum):
    Root = 0
    Stem = 1
    TrueFalse = 2
    Integer = 3
    Combo = 4
    Float = 5
    String = 6
    Button = 7


class ConfigTreeItem(QTreeWidgetItem):
    combobox: Union[QComboBox, None]
    spinbox: Union[QSpinBox, CustomDoubleSpinBox, None]
    lineedit: Union[QLineEdit, None]
    level: int
    description: str = ''

    def __init__(self, propname: str = '', proptype: int = PropType.TrueFalse, itemEnable: bool = True, level: int = 0):
        super().__init__()
        self.combobox = None
        self.spinbox = None
        self.lineedit = None
        self.button = None
        self.level = level
        self.name = propname
        self.setText(0, self.name)
        if proptype == PropType.TrueFalse:
            self.combobox = QComboBox()
            self.combobox.addItems(['False', 'True'])
            self.combobox.setEnabled(itemEnable)
            self.combobox.wheelEvent = self.onWheelEvent
        elif proptype == PropType.Integer:
            self.spinbox = QSpinBox()
            self.spinbox.setEnabled(itemEnable)
            self.spinbox.wheelEvent = self.onWheelEvent
        elif proptype == PropType.Combo:
            self.combobox = QComboBox()
            self.combobox.setEnabled(itemEnable)
            self.combobox.wheelEvent = self.onWheelEvent
        elif proptype == PropType.Float:
            self.spinbox = CustomDoubleSpinBox()
            self.spinbox.setEnabled(itemEnable)
            self.spinbox.wheelEvent = self.onWheelEvent
        elif proptype == PropType.String:
            self.lineedit = QLineEdit()
            self.lineedit.setEnabled(itemEnable)
            self.lineedit.editingFinished.connect(self.onLineEditEditingFinished)
            self.lineedit.setFrame(False)
        elif proptype == PropType.Button:
            self.button = QPushButton('Action')
            self.button.setIcon(QIcon('./Resource/arrow_command.png'))
            self.button.setEnabled(itemEnable)

    def onWheelEvent(self, event):
        pass

    def setDisabled(self, disabled: bool) -> None:
        if self.combobox is not None:
            self.combobox.setEnabled(not disabled)
        if self.spinbox is not None:
            self.spinbox.setEnabled(not disabled)
        if self.lineedit is not None:
            self.lineedit.setEnabled(not disabled)
        if self.button is not None:
            self.button.setEnabled(not disabled)
        QTreeWidgetItem.setDisabled(self, disabled)

    def onLineEditEditingFinished(self):
        pass

    def setBoolean(self, value: bool):
        if self.combobox is not None:
            self.combobox.setCurrentIndex(int(value))

    def getBoolean(self) -> bool:
        if self.combobox is not None:
            return bool(self.combobox.currentIndex())
        return False
