import os
import time
import json
from datetime import datetime
from typing import Union, Tuple
from threading import Thread
from pynput.mouse import Controller as MouseController
# from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Listener as KeyboardListener
from pynput.keyboard import Key, KeyCode
from Task import *
from Util import GetLogger, Callback, ensure_path_exist
PROJ_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
            "minimize_when_executing": True,
            "last_job_file_path": "",
            "record_mouse_position_fn_key": "F10"
        }
        ensure_path_exist(CFG_PATH)
        self._default_app_config_file_path = os.path.join(CFG_PATH, "app_config.json")
        self._record_mouse_pos_key: KeyCode = Key.f10
        self._record_key_seqeunce_key: KeyCode = Key.f10
        self._recording_key_sequence: bool = False

        self.load_config()

        self.sig_monitor_result = Callback(dict)
        self.sig_job_task_list_changed = Callback()
        self.sig_task_properties_modified = Callback(Task)
        self.sig_job_execute_started = Callback(dict)
        self.sig_job_execute_terminated = Callback()
        self.sig_job_current_task_index = Callback(int)

        self._mouse_controller = MouseController()
        self._keyboard_controller = KeyboardController()
        self._keyboard_listner = KeyboardListener(on_press=self._on_key_press, on_release=self._on_key_release)
        self._keyboard_listner.start()
        self._current_mouse_pos: Tuple[int, int] = (0, 0)

        self._job = MacroJob("no_named")
        self._job.set_mouse_controller(self._mouse_controller)
        self._job.set_keyboard_controller(self._keyboard_controller)
        self._job.sig_task_list_changed.connect(self.sig_job_task_list_changed.emit)
        self._job.sig_execute_started.connect(self._on_job_execute_started)
        self._job.sig_execute_terminated.connect(self._on_job_execute_terminated)
        self._job.sig_current_executing_task_index.connect(self._on_job_current_executing_task_index)
        self.load_job_file(self._config.get("last_job_file_path", ""))
        self._current_editing_task_index: int = -1

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

        try:
            self._record_mouse_pos_key = Key[self._config.get("record_mouse_position_fn_key", "F10").lower()]
        except Exception as e:
            GetLogger().critical(f"failed to set record mouse pos key: {e}", self)
            self._record_mouse_pos_key = Key.f10
            self._config["record_mouse_position_fn_key"] = "F10"

    def save_config(self):
        try:
            with open(self._default_app_config_file_path, "w") as fp:
                json.dump(self._config, fp, indent=4)
        except Exception as e:
            GetLogger().critical(f"failed to save config: {e}", self)

    def load_job_file(self, file_path: str) -> bool:
        if self._job.set_file_path(file_path):
            result = self._job.load()
            if result:
                self._config["last_job_file_path"] = self._job.file_path
            return result
        return False

    def save_job_file(self, file_path: str):
        self._job.save_as(file_path)

    def execute_job(self, repeat_count: int, infinite: bool = False):
        self._job.repeat_count = 0 if infinite else repeat_count
        self._job.execute()
        self.save_config()

    def stop_job(self):
        self._job.stop()

    def _on_job_execute_started(self):
        self.sig_job_execute_started.emit(self._config)

    def _on_job_execute_terminated(self):
        self.sig_job_execute_terminated.emit()

    def _on_job_current_executing_task_index(self, index: int):
        self.sig_job_current_task_index.emit(index)

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
        if "mouse_pos" in result.keys():
            self._current_mouse_pos = result.get("mouse_pos")
        self.sig_monitor_result.emit(result)

    def _on_thread_monitor_terminated(self):
        del self._thread_monitor
        self._thread_monitor = None

    def _on_key_press(self, key: Union[Key, KeyCode, None]):
        if self._recording_key_sequence:
            task = self.get_current_editing_task()
            if isinstance(task, TaskKeyboardSequence):
                task.add_sequence_press(key)

    def _on_key_release(self, key: Union[Key, KeyCode, None]):
        if self._recording_key_sequence:
            task = self.get_current_editing_task()
            if isinstance(task, TaskKeyboardSequence):
                task.add_sequence_release(key)
        else:
            if key == self._record_mouse_pos_key:
                task = self.get_current_editing_task()
                if isinstance(task, TaskMouseCommon):
                    task.pos_x = self._current_mouse_pos[0]
                    task.pos_y = self._current_mouse_pos[1]
                    self.sig_task_properties_modified.emit(task)
            elif key == Key.esc:
                self._job.stop()

    def get_current_editing_task(self) -> Union[Task, None]:
        if 0 <= self._current_editing_task_index < len(self._job.task_list):
            return self._job.task_list[self._current_editing_task_index]
        return None

    def move_mouse_cursor_to(self, x: int, y: int):
        self._mouse_controller.position = x, y

    @property
    def job(self) -> MacroJob:
        return self._job

    @property
    def config(self) -> dict:
        return self._config

    @property
    def current_mouse_pos(self) -> Tuple[int, int]:
        return self._current_mouse_pos

    @property
    def current_editing_task_index(self) -> int:
        return self._current_editing_task_index

    @current_editing_task_index.setter
    def current_editing_task_index(self, index: int):
        self._current_editing_task_index = index

    @property
    def record_mouse_pos_key(self) -> KeyCode:
        return self._record_mouse_pos_key

    @property
    def recording_key_sequence(self) -> bool:
        return self._recording_key_sequence

    @recording_key_sequence.setter
    def recording_key_sequence(self, value: bool):
        self._recording_key_sequence = value
