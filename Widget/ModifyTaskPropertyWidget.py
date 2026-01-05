import os
import sys
from functools import partial
from typing import Union, List
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (QWidget, QTreeWidget, QLabel, QPushButton,
                               QVBoxLayout, QHBoxLayout, QSizePolicy)
CUR_PATH = os.path.dirname(os.path.abspath(__file__))  # {PROJ}/Widget
PROJ_PATH = os.path.dirname(CUR_PATH)
sys.path.extend([CUR_PATH, PROJ_PATH])
sys.path = list(set(sys.path))
from AppCore import AppCore
from Task import *
from Util import PropType, ConfigTreeItem


class ModifyTaskPropertyWidget(QWidget):
    _core: AppCore = None
    sig_task_property_changed = Signal(Task)
    sig_record_key_sequence_started = Signal()
    sig_record_key_sequence_stopped = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._tree = QTreeWidget()
        self._treeitems: List[ConfigTreeItem] = list()
        self._lbl_current_mouse_position = QLabel()
        self.initControl()
        self.initLayout()

    def initLayout(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(self._tree)
        vbox.addWidget(self._lbl_current_mouse_position)

        subwgt = QWidget()
        subwgt.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        hbox = QHBoxLayout(subwgt)
        hbox.setContentsMargins(2, 0, 0, 0)
        hbox.addWidget(self._lbl_current_mouse_position)
        vbox.addWidget(subwgt)

        self._lbl_current_mouse_position.hide()

    def initControl(self):
        self._tree.setColumnCount(2)
        self._tree.setHeaderLabels(['Properties', 'Value'])
        self._tree.setStyleSheet("QTreeView:item {border:0.5px; border-style:solid; \
                                                          border-color:lightgray; border-top: none; border-left: none} \
                                          QTreeView:item:selected {background: #CDE8FF; selection-color: black}")
        self._tree.setColumnWidth(0, 100)
        self._tree.setIndentation(0)

    def setCore(self, core: AppCore):
        self._core = core

    def updateControl(self):
        pass

    def updateMousePosition(self, pos_x: int, pos_y: int):
        self._lbl_current_mouse_position.setText(f"Press {self._core.record_mouse_pos_key.name.upper()} to Change Mouse Position (X: {pos_x}, Y: {pos_y})")

    def setTask(self, task: Union[Task, None]):
        self._tree.clear()
        self._treeitems.clear()
        self._lbl_current_mouse_position.hide()
        if task is None:
            self.setVisible(False)
            return
        self.setVisible(True)

        item = ConfigTreeItem("Name", PropType.String)
        item.lineedit.setText(task.name)
        self._tree.addTopLevelItem(item)
        self._tree.setItemWidget(item, 1, item.lineedit)
        self._treeitems.append(item)
        if task.type == TaskType.SLEEP:
            item = ConfigTreeItem("Time (sec)", PropType.Float)
            item.spinbox.setRange(0, 0xFFFF)
            item.spinbox.setDecimals(3)
            item.spinbox.setValue(task.sleep_time_sec)
            item.spinbox.valueChanged.connect(partial(self._onItemSpinboxSleepTimeValueChanged, task))
            self._tree.addTopLevelItem(item)
            self._tree.setItemWidget(item, 1, item.spinbox)
            self._treeitems.append(item)
        elif task.type in [TaskType.MOUSE_MOVE, TaskType.MOUSE_LEFT_CLICK, TaskType.MOUSE_LEFT_DOUBLE_CLICK,
                           TaskType.MOUSE_RIGHT_CLICK, TaskType.MOUSE_RIGHT_DOUBLE_CLICK,
                           TaskType.MOUSE_LEFT_PRESS, TaskType.MOUSE_LEFT_RELEASE,
                           TaskType.MOUSE_RIGHT_PRESS, TaskType.MOUSE_RIGHT_RELEASE]:
            item = ConfigTreeItem("POS X", PropType.Integer)
            item.spinbox.setRange(0, 0xFFFF)
            item.spinbox.setValue(task.pos_x)
            item.spinbox.valueChanged.connect(partial(self._onItemSpinboxPosXValueChanged, task))
            self._tree.addTopLevelItem(item)
            self._tree.setItemWidget(item, 1, item.spinbox)
            self._treeitems.append(item)
            item = ConfigTreeItem("POS Y", PropType.Integer)
            item.spinbox.setRange(0, 0xFFFF)
            item.spinbox.setValue(task.pos_y)
            item.spinbox.valueChanged.connect(partial(self._onItemSpinboxPosYValueChanged, task))
            self._tree.addTopLevelItem(item)
            self._tree.setItemWidget(item, 1, item.spinbox)
            self._treeitems.append(item)
            self._lbl_current_mouse_position.show()
        elif task.type == TaskType.MOUSE_SCROLL:
            item = ConfigTreeItem("DISP X", PropType.Integer)
            item.spinbox.setRange(0, 0xFFFF)
            item.spinbox.setValue(task.dx)
            item.spinbox.valueChanged.connect(partial(self._onItemSpinboxScrollXValueChanged, task))
            self._tree.addTopLevelItem(item)
            self._tree.setItemWidget(item, 1, item.spinbox)
            self._treeitems.append(item)
            item = ConfigTreeItem("DISP Y", PropType.Integer)
            item.spinbox.setRange(0, 0xFFFF)
            item.spinbox.setValue(task.dy)
            item.spinbox.valueChanged.connect(partial(self._onItemSpinboxScrollYValueChanged, task))
            self._tree.addTopLevelItem(item)
            self._tree.setItemWidget(item, 1, item.spinbox)
            self._treeitems.append(item)
        elif task.type == TaskType.KEY_SEQUENCE:
            item = ConfigTreeItem("Sequence", PropType.String)
            item.lineedit.setEnabled(False)
            item.lineedit.setText(task.to_string())
            self._tree.addTopLevelItem(item)
            self._tree.setItemWidget(item, 1, item.lineedit)
            self._treeitems.append(item)
            item = ConfigTreeItem("Record", PropType.Button)
            item.button.setText("Start")
            item.button.setIcon(QIcon("./Resource/Icon/record.png"))
            item.button.clicked.connect(partial(self._onItemButtonRecordClicked, item.button, task))
            self._tree.addTopLevelItem(item)
            self._tree.setItemWidget(item, 1, item.button)
            self._treeitems.append(item)

        # self._setFontSize(10)

    def _setFontSize(self, size: int):
        font = QFont()
        font.setPointSize(size)
        font.setFamily('Arial')
        for item in self._treeitems:
            item.setFont(0, font)
            item.setFont(1, font)
            if item.combobox is not None:
                item.combobox.setFont(font)
            if item.spinbox is not None:
                item.spinbox.setFont(font)
                lineedit = item.spinbox.lineEdit()
                lineedit.setFont(font)
            if item.button is not None:
                item.button.setFont(font)
            if item.lineedit is not None:
                item.lineedit.setFont(font)
        w, h = self._tree.size().width(), self._tree.size().height()
        self._tree.resize(w, h - 1)
        self._tree.resize(w, h)

    def _onItemSpinboxSleepTimeValueChanged(self, task: TaskSleep, value: float):
        if task.sleep_time_sec != value:
            task.sleep_time_sec = value
            self.sig_task_property_changed.emit(task)

    def _onItemSpinboxPosXValueChanged(self, task: TaskMouseCommon, value: int):
        if task.pos_x != value:
            task.pos_x = value
            self.sig_task_property_changed.emit(task)

    def _onItemSpinboxPosYValueChanged(self, task: TaskMouseCommon, value: int):
        if task.pos_y != value:
            task.pos_y = value
            self.sig_task_property_changed.emit(task)

    def _onItemSpinboxScrollXValueChanged(self, task: TaskMouseScroll, value: int):
        if task.dx != value:
            task.dx = value
            self.sig_task_property_changed.emit(task)

    def _onItemSpinboxScrollYValueChanged(self, task: TaskMouseScroll, value: int):
        if task.dy != value:
            task.dy = value
            self.sig_task_property_changed.emit(task)

    def _onItemButtonRecordClicked(self, button: QPushButton, task: TaskKeySequence):
        if not self._core.recording_key_sequence:
            self.sig_record_key_sequence_started.emit()
            task.clear_sequence()
            self._core.recording_key_sequence = True
            button.setText("Stop")
            button.setIcon(QIcon("./Resource/Icon/stop.png"))
        else:
            self.sig_record_key_sequence_stopped.emit()
            self._core.recording_key_sequence = False
            button.setText("Start")
            button.setIcon(QIcon("./Resource/Icon/record.png"))
            self.sig_task_property_changed.emit(task)
