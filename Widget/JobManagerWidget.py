import os
import sys
from functools import partial
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QWheelEvent
from PySide6.QtWidgets import (QWidget, QPushButton, QComboBox, QLineEdit,
                               QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QAbstractItemDelegate,
                               QVBoxLayout, QHBoxLayout, QSizePolicy)
CUR_PATH = os.path.dirname(os.path.abspath(__file__))  # {PROJ}/Widget
PROJ_PATH = os.path.dirname(CUR_PATH)
sys.path.extend([CUR_PATH, PROJ_PATH])
sys.path = list(set(sys.path))
from AppCore import AppCore
from Task import *
from ModifyTaskPropertyWidget import ModifyTaskPropertyWidget


class JobManagerWidget(QWidget):
    _core: AppCore = None

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._widget_control_task = QWidget()
        self._widget_modify_task_property = ModifyTaskPropertyWidget(self)
        self._btn_add_task = QPushButton()
        self._btn_remove_task = QPushButton()
        self._btn_clear_task = QPushButton()
        self._btn_move_task_up = QPushButton()
        self._btn_move_task_down = QPushButton()
        self._table_task_list = QTableWidget()
        self.initControl()
        self.initLayout()

    def initLayout(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(4)

        self._widget_control_task = QWidget()
        self._widget_control_task.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        hbox = QHBoxLayout(self._widget_control_task)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(4)
        hbox.addWidget(self._btn_add_task)
        hbox.addWidget(self._btn_remove_task)
        hbox.addWidget(self._btn_move_task_up)
        hbox.addWidget(self._btn_move_task_down)
        hbox.addWidget(self._btn_clear_task)
        hbox.addWidget(QWidget())
        vbox.addWidget(self._widget_control_task)
        vbox.addWidget(self._table_task_list)
        vbox.addWidget(self._widget_modify_task_property)
        self._widget_modify_task_property.setVisible(False)

    def initControl(self):
        self._btn_add_task.setIcon(QIcon("./Resource/Icon/plus.png"))
        self._btn_add_task.clicked.connect(self._onClickBtnAddTask)
        self._btn_add_task.setIconSize(QSize(22, 22))
        self._btn_add_task.setFixedSize(24, 24)
        self._btn_add_task.setFlat(True)
        self._btn_add_task.setToolTip("Add Task")
        self._btn_remove_task.setIcon(QIcon("./Resource/Icon/minus.png"))
        self._btn_remove_task.clicked.connect(self._onClickBtnRemoveTask)
        self._btn_remove_task.setIconSize(QSize(22, 22))
        self._btn_remove_task.setFixedSize(24, 24)
        self._btn_remove_task.setFlat(True)
        self._btn_remove_task.setToolTip("Remove Task")
        self._btn_move_task_up.setIcon(QIcon("./Resource/Icon/arrow_up.png"))
        self._btn_move_task_up.clicked.connect(self._onClickBtnMoveTaskUp)
        self._btn_move_task_up.setIconSize(QSize(22, 22))
        self._btn_move_task_up.setFixedSize(24, 24)
        self._btn_move_task_up.setFlat(True)
        self._btn_move_task_up.setToolTip("Move Task Up")
        self._btn_move_task_down.setIcon(QIcon("./Resource/Icon/arrow_down.png"))
        self._btn_move_task_down.clicked.connect(self._onClickBtnMoveTaskDown)
        self._btn_move_task_down.setIconSize(QSize(22, 22))
        self._btn_move_task_down.setFixedSize(24, 24)
        self._btn_move_task_down.setFlat(True)
        self._btn_move_task_down.setToolTip("Move Task Down")
        self._btn_clear_task.setIcon(QIcon("./Resource/Icon/clear.png"))
        self._btn_clear_task.clicked.connect(self._onClickBtnClearTask)
        self._btn_clear_task.setIconSize(QSize(22, 22))
        self._btn_clear_task.setFixedSize(24, 24)
        self._btn_clear_task.setFlat(True)
        self._btn_clear_task.setToolTip("Clear Task(s)")

        hlabels = ["type", "name"]
        self._table_task_list.setColumnCount(len(hlabels))
        self._table_task_list.setHorizontalHeaderLabels(hlabels)
        hHeader = self._table_task_list.horizontalHeader()
        hHeader.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hHeader.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table_task_list.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table_task_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table_task_list.itemSelectionChanged.connect(self._onTableTaskListItemSelectionChanged)
        self._table_task_list.closeEditor = self._onTableTaskListCloseEditor

        self._widget_modify_task_property.sig_task_property_changed.connect(self._onTaskPropertyChanged)

    def setCore(self, core: AppCore):
        self._core = core
        self._widget_modify_task_property.setCore(self._core)
        self.drawTaskList()

    def updateControl(self):
        job = self._core.job
        self._widget_control_task.setEnabled(not job.is_executing())
        self._table_task_list.setEnabled(not job.is_executing())
        if self._core.current_editing_task_index >= 0:
            self._btn_remove_task.setEnabled(True)
            self._btn_move_task_up.setEnabled(True)
            self._btn_move_task_down.setEnabled(True)
            if self._core.current_editing_task_index == 0:
                self._btn_move_task_up.setEnabled(False)
            elif self._core.current_editing_task_index == len(job.task_list) - 1:
                self._btn_move_task_down.setEnabled(False)
        else:
            self._btn_remove_task.setEnabled(False)
            self._btn_move_task_up.setEnabled(False)
            self._btn_move_task_down.setEnabled(False)

    def updateMousePosition(self, pos_x: int, pos_y: int):
        self._widget_modify_task_property.updateMousePosition(pos_x, pos_y)

    def drawTaskList(self):
        job = self._core.job
        task_list = job.task_list
        self._table_task_list.setRowCount(len(task_list))
        for r, task in enumerate(task_list):
            combo = self._table_task_list.cellWidget(r, 0)
            if combo is None:
                combo = QComboBox()
                combo.addItems([x.name for x in TaskType][1:])
                combo.currentIndexChanged.connect(partial(self._onComboTaskTypeIndexChanged, r))
                combo.wheelEvent = self._onComboTaskTypeWheelEvent
                self._table_task_list.setCellWidget(r, 0, combo)
            combo.setCurrentIndex(task.type.value - 1)

            item = self._table_task_list.item(r, 1)
            if item is None:
                item = QTableWidgetItem()
                self._table_task_list.setItem(r, 1, item)
            item.setText(task.name)

    def _onClickBtnAddTask(self):
        job = self._core.job
        job.add_task(TaskSleep("delay", 1))
        # todo: toggle add task job window?

    def _onClickBtnRemoveTask(self):
        job = self._core.job
        task = self._core.get_current_editing_task()
        if task is not None:
            job.remove_task(task)

    def _onClickBtnMoveTaskUp(self):
        job = self._core.job
        idx1 = self._core.current_editing_task_index - 1
        idx2 = idx1 + 1
        if 0 <= idx1:
            job.switch_task(idx1, idx2)
            self._table_task_list.selectRow(idx1)

    def _onClickBtnMoveTaskDown(self):
        job = self._core.job
        idx1 = self._core.current_editing_task_index
        idx2 = idx1 + 1
        if idx1 < len(job.task_list) - 1:
            job.switch_task(idx1, idx2)
            self._table_task_list.selectRow(idx2)

    def _onClickBtnClearTask(self):
        job = self._core.job
        job.clear_task()

    def _onTableTaskListItemSelectionChanged(self):
        sel_items = self._table_task_list.selectedItems()
        rows = list(set([x.row() for x in sel_items]))
        if len(rows) > 0:
            index = rows[0]
        else:
            index = -1
        if self._core.current_editing_task_index != index:
            self._core.current_editing_task_index = index
            self._refreshTaskPropertyWidget()

    def _onTableTaskListCloseEditor(self, editor: QLineEdit, hint: QAbstractItemDelegate.EndEditHint):
        if hint == QAbstractItemDelegate.EndEditHint.SubmitModelCache:
            text = editor.text()
            job = self._core.job
            job.set_task_name(self._core.current_editing_task_index, text)
            self._refreshTaskPropertyWidget()
        QTableWidget.closeEditor(self._table_task_list, editor, hint)

    def _onComboTaskTypeIndexChanged(self, task_index: int, combo_index: int):
        job = self._core.job
        task = job.task_list[task_index]
        if task.type.value != combo_index + 1:
            new_task = create_task(TaskType(combo_index + 1))
            job.replace_task(task_index, new_task)
            self._refreshTaskPropertyWidget()

    def _onComboTaskTypeWheelEvent(self, event: QWheelEvent):
        # ignore wheel event
        pass

    def _refreshTaskPropertyWidget(self):
        task = self._core.get_current_editing_task()
        self._widget_modify_task_property.setTask(task)
        self._widget_modify_task_property.setVisible(task is not None)

    def _onTaskPropertyChanged(self, task: Task):
        pass

    def updateTaskProperty(self, task: Task):
        self._refreshTaskPropertyWidget()
