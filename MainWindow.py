import queue
import time
from datetime import datetime
from typing import Union
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel, QPushButton,
                               QVBoxLayout, QHBoxLayout, QMenuBar, QMenu, QStatusBar)
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
        self._update_timer_sec = 0.1

    def run(self):
        GetLogger().info("Started", self)
        cur_time = time.perf_counter()
        while self._keep_alive:
            if not self._queue.empty():
                obj: dict = self._queue.get()
                self.sig_update_from_queue.emit(obj)

            elapsed = time.perf_counter() - cur_time
            if elapsed >= self._update_timer_sec:
                self.sig_update_by_timer.emit()
                cur_time = time.perf_counter()

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
        self._widget_job_manager = JobManagerWidget(self)
        self._btn_start = QPushButton("START")
        self._btn_stop = QPushButton("STOP")
        self._lbl_app_version = QLabel()
        self._lbl_app_build_date = QLabel()
        self._lbl_time_stamp = QLabel()
        self._queue_update_control = queue.Queue()
        self.setWindowTitle("MACRO")
        self.setWindowIcon(QIcon("./Resource/Icon/application.ico"))
        self.initControl()
        self.initLayout()
        self.initMenuBar()
        self.initStatusBar()

        self._startThreadUpdateControl()
        GetLogger().info("Initialized", self)

    def initLayout(self):
        cental = QWidget()
        self.setCentralWidget(cental)

        vbox = QVBoxLayout(cental)
        vbox.setContentsMargins(4, 4, 4, 4)
        vbox.setSpacing(4)
        vbox.addWidget(self._widget_job_manager)

        subwgt = QWidget()
        hbox = QHBoxLayout(subwgt)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(4)
        hbox.addWidget(self._btn_start)
        hbox.addWidget(self._btn_stop)
        vbox.addWidget(subwgt)

    def initControl(self):
        self._btn_start.setIcon(QIcon("./Resource/Icon/play.png"))
        self._btn_start.clicked.connect(self._onClickBtnStart)
        self._btn_stop.setIcon(QIcon("./Resource/Icon/stop.png"))
        self._btn_stop.clicked.connect(self._onClickBtnStop)

    def initMenuBar(self):
        menubar = QMenuBar()
        self.setMenuBar(menubar)
        menubar.setNativeMenuBar(False)

        menu_file = QMenu("File", parent=menubar)
        menubar.addAction(menu_file.menuAction())

        menu_option = QMenu("Option", parent=menubar)
        menubar.addAction(menu_option.menuAction())

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
        self._core.sig_job_task_list_changed.connect(
            lambda: self._putUpdateControlQueue({"task_list_changed": True}))
        self._widget_job_manager.setCore(self._core)

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
            self._thread_update_control.sig_update_by_timer.connect(self._onThreadUpdateUpdateControlByTimer)
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

        task_list_changed = obj.get("task_list_changed", False)
        if task_list_changed:
            self._widget_job_manager.drawTaskList()

    def _onThreadUpdateUpdateControlByTimer(self):
        job = self._core.job
        self._btn_start.setEnabled(not job.is_executing())
        self._btn_stop.setEnabled(job.is_executing())
        self._widget_job_manager.updateControl()

    def _putUpdateControlQueue(self, obj: dict):
        if self._queue_update_control.empty() and self._recv_monitor_result:
            self._queue_update_control.put(obj)

    def _onClickBtnStart(self):
        job = self._core.job
        job.execute()

    def _onClickBtnStop(self):
        job = self._core.job
        job.stop()


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
