import os
import time
import json
from datetime import datetime
from typing import Union
from threading import Thread
from pynput.mouse import Controller as MouseController
# from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Listener as KeyboardListener
from pynput.keyboard import Key, KeyCode
from Task import *
from Util import GetLogger, Callback, ensure_path_exist
PROJ_PATH = os.path.dirname(os.path.abspath(__file__))
CFG_PATH = os.path.join(PROJ_PATH, "Config")


class ThreadMonitor(Thread):
    _keep_alive: bool = True

    def __init__(self, mouse_controller: MouseController):
        Thread.__init__(self)
        self.daemon = True
        self._current_mouse_pos = (0, 0)
        self._mouse_controller = mouse_controller

        self.sig_result = Callback(dict)
        self.sig_terminated = Callback()

    def run(self):
        GetLogger().info("Started", self)
        timestamp_check_time = time.perf_counter()
        while self._keep_alive:
            result = {}
            cur_time = time.perf_counter()

            # current mouse position
            mouse_pos = self._mouse_controller.position
            if self._current_mouse_pos != mouse_pos:
                result["mouse_pos"] = mouse_pos[0], mouse_pos[1]
                self._current_mouse_pos = mouse_pos

            # current timestamp
            if cur_time - timestamp_check_time >= 0.1:
                result["timestamp"] = datetime.now()
                timestamp_check_time = cur_time

            if len(result) > 0:
                self.sig_result.emit(result)
            time.sleep(1e-3)
        self.sig_terminated.emit()
        GetLogger().info("Terminated", self)

    def stop(self):
        self._keep_alive = False


class AppCore:
    _thread_monitor: Union[ThreadMonitor, None] = None

    def __init__(self):
        super().__init__()
        self._config = {
            "minimize_when_executing": True
        }
        ensure_path_exist(CFG_PATH)
        self._default_app_config_file_path = os.path.join(CFG_PATH, "app_config.json")
        self.load_config()

        self.sig_monitor_result = Callback(dict)
        self.sig_job_task_list_changed = Callback()

        self._mouse_controller = MouseController()
        self._keyboard_controller = KeyboardController()
        self._keyboard_listner = KeyboardListener(on_press=self._on_key_press, on_release=self._on_key_release)
        self._keyboard_listner.start()

        self._job = MacroJob("no_named")
        self._job.set_mouse_controller(self._mouse_controller)
        self._job.set_keyboard_controller(self._keyboard_controller)
        self._job.sig_task_list_changed.connect(self.sig_job_task_list_changed.emit)
        self._job.load()

        self._start_thread_monitor()

    def release(self):
        self._keyboard_listner.stop()
        self._stop_thread_monitor()
        self._job.save()
        self.save_config()

    def load_config(self):
        try:
            if not os.path.isfile(self._default_app_config_file_path):
                self.save_config()
            with open(self._default_app_config_file_path, "r") as fp:
                self._config = json.load(fp)
        except Exception as e:
            GetLogger().critical(f"failed to load config: {e}", self)

    def save_config(self):
        try:
            with open(self._default_app_config_file_path, "w") as fp:
                json.dump(self._config, fp, indent=4)
        except Exception as e:
            GetLogger().critical(f"failed to save config: {e}", self)

    def load_job_file(self, file_path: str):
        self._job.set_file_path(file_path)
        self._job.load()

    def save_job_file(self, file_path: str):
        self._job.save_as(file_path)

    def _start_thread_monitor(self):
        if self._thread_monitor is None:
            self._thread_monitor = ThreadMonitor(self._mouse_controller)
            self._thread_monitor.sig_result.connect(self._on_thread_monitor_result)
            self._thread_monitor.sig_terminated.connect(self._on_thread_monitor_terminated)
            self._thread_monitor.start()

    def _stop_thread_monitor(self):
        if self._thread_monitor is not None:
            self._thread_monitor.stop()

    def _on_thread_monitor_result(self, result: dict):
        self.sig_monitor_result.emit(result)

    def _on_thread_monitor_terminated(self):
        del self._thread_monitor
        self._thread_monitor = None

    def _on_key_press(self, key: Union[Key, KeyCode, None]):
        pass

    def _on_key_release(self, key: Union[Key, KeyCode, None]):
        pass

    @property
    def job(self) -> MacroJob:
        return self._job

    @property
    def config(self) -> dict:
        return self._config
