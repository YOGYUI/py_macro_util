import queue
from datetime import datetime
from typing import Union
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel,
                               QVBoxLayout, QStatusBar)
from Widget import *
from AppCore import AppCore
from Util import GetLogger


class ThreadUpdateControl(QThread):
    _keep_alive: bool = True
    sig_update_from_queue = Signal(dict)
    sig_update_by_timer = Signal()
    sig_terminated = Signal()

    def __init__(self, q: queue.Queue):
        super().__init__()
        self._queue = q

    def run(self):
        GetLogger().info("Started", self)
        while self._keep_alive:
            if not self._queue.empty():
                obj: dict = self._queue.get()
                self.sig_update_from_queue.emit(obj)

            self.msleep(10)
        GetLogger().info("Terminated", self)
        self.sig_terminated.emit()
        self.deleteLater()

    def stop(self):
        self._keep_alive = False


class MainWindow(QMainWindow):
    _core: AppCore = None
    _recv_monitor_result: bool = True
    _thread_update_control: Union[ThreadUpdateControl, None] = None

    def __init__(self):
        super().__init__()
        self._widget_task_list_table = TaskListTableWidget(self)
        self._lbl_app_version = QLabel()
        self._lbl_app_build_date = QLabel()
        self._lbl_time_stamp = QLabel()
        self._queue_update_control = queue.Queue()
        self.setWindowTitle("MACRO")
        self.setWindowIcon(QIcon("./Resource/Icon/application.ico"))
        self.initControl()
        self.initLayout()
        self.initStatusBar()

        self._startThreadUpdateControl()
        GetLogger().info("Initialized", self)

    def initLayout(self):
        cental = QWidget()
        self.setCentralWidget(cental)

        vbox = QVBoxLayout(cental)
        vbox.setContentsMargins(4, 4, 4, 4)
        vbox.setSpacing(4)
        vbox.addWidget(self._widget_task_list_table)

    def initControl(self):
        pass

    def initStatusBar(self):
        statusbar = QStatusBar(self)
        self.setStatusBar(statusbar)
        statusbar.addWidget(self._lbl_app_version)
        statusbar.addWidget(self._lbl_app_build_date)
        statusbar.addPermanentWidget(self._lbl_time_stamp)

    def release(self):
        self._recv_monitor_result = False
        self._stopThreadUpdateControl()
        GetLogger().info("Released", self)

    def setCore(self, core: AppCore):
        self._core = core
        self._core.sig_monitor_result.connect(self._putUpdateControlQueue)
        self._widget_task_list_table.setCore(self._core)

    def setVersionInfo(self, info: dict):
        self._lbl_app_version.setText(f"version: {info.get('version', '?.?.?')}")
        self._lbl_app_build_date.setText(f"build: {info.get('build_date', '?.?.?')}")

    def onWindowMessage(self, msg: int):
        if msg == 1025:  # WM_USER + 1
            self.show()
            self.showNormal()
            self.activateWindow()

    def _startThreadUpdateControl(self):
        if self._thread_update_control is None:
            self._thread_update_control = ThreadUpdateControl(self._queue_update_control)
            self._thread_update_control.sig_update_from_queue.connect(self._onThreadUpdateControlUpdateFromQueue)
            self._thread_update_control.sig_terminated.connect(self._onThreadUpdateControlTerminated)
            self._thread_update_control.start()

    def _stopThreadUpdateControl(self):
        if self._thread_update_control is not None:
            self._thread_update_control.stop()
            while self._thread_update_control.isRunning():
                pass

    def _onThreadUpdateControlTerminated(self):
        self._thread_update_control = None

    def _onThreadUpdateControlUpdateFromQueue(self, obj: dict):
        if "timestamp" in obj.keys():
            timestamp: datetime = obj.get("timestamp")
            self._lbl_time_stamp.setText(timestamp.strftime("%Y-%m-%d %H:%M:%S"))

        if "mouse_position" in obj.keys():
            pos_x, pos_y = obj.get("mouse_position")

    def _putUpdateControlQueue(self, obj: dict):
        if self._queue_update_control.empty() and self._recv_monitor_result:
            self._queue_update_control.put(obj)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    abspath = os.path.dirname(os.path.abspath(__file__))
    os.chdir(abspath)

    QApplication.setStyle('fusion')
    app = QApplication(sys.argv)
    core_ = AppCore()
    wnd_ = MainWindow()
    wnd_.setCore(core_)
    wnd_.show()
    app.exec()
    wnd_.release()
    core_.release()
