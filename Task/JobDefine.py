import os
import sys
import json
from typing import List, Union
from threading import Thread
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController
from TaskDefine import (Task, load_task_from_dict)
CUR_PATH = os.path.dirname(os.path.abspath(__file__))  # {PROJ}/Task
PROJ_PATH = os.path.dirname(CUR_PATH)
CFG_PATH = os.path.join(PROJ_PATH, "Config")
sys.path.extend([CUR_PATH, PROJ_PATH])
sys.path = list(set(sys.path))
from Util import Callback, GetLogger


class ThreadExecute(Thread):
    _keep_alive: bool = True

    def __init__(self, task_list: List[Task], repeat_count: int):
        Thread.__init__(self)
        self.daemon = True
        self._task_list = task_list
        self._repeat_count = repeat_count
        self.sig_terminated = Callback()
        self.sig_current_task_index = Callback(int)

    def run(self):
        index: int = 0
        seq_count: int = 0
        GetLogger().info(f"Started (repeat count: {self._repeat_count})", self)
        while True:
            if not self._keep_alive:
                break
            try:
                if index < len(self._task_list):
                    task = self._task_list[index]
                    self.sig_current_task_index.emit(index)
                    task.execute()
                index += 1
                if index >= len(self._task_list):
                    index = 0
                    if self._repeat_count > 0:
                        seq_count += 1
                        if seq_count >= self._repeat_count:
                            break
            except Exception as e:
                GetLogger().critical(f"Exception: {e}", self)
        GetLogger().info("Terminated", self)
        self.sig_terminated.emit()

    def stop(self):
        self._keep_alive = False


class MacroJob:
    _mouse_controller: Union[MouseController, None] = None
    _keyboard_controller: Union[KeyboardController, None] = None
    _thread_execute: Union[ThreadExecute, None] = None

    def __init__(self, name: str):
        super().__init__()
        self._name = name
        self._task_list: List[Task] = list()
        self._repeat_count: int = 1
        self._file_path: str = os.path.join(CFG_PATH, "default_job.json")

        self.sig_task_list_changed = Callback()
        self.sig_current_executing_task_index = Callback(int)
        self.sig_execute_started = Callback()
        self.sig_execute_terminated = Callback()

    def set_mouse_controller(self, controller: MouseController):
        self._mouse_controller = controller
        self.refresh_task(False)

    def set_keyboard_controller(self, controller: KeyboardController):
        self._keyboard_controller = controller
        self.refresh_task(False)

    def execute(self):
        self.save()
        self._start_thread_execute()

    def pause(self):
        pass

    def stop(self):
        self._stop_thread_execute()

    def is_executing(self) -> bool:
        return self._thread_execute is not None and self._thread_execute.is_alive()

    def _start_thread_execute(self):
        if self._thread_execute is None:
            self._thread_execute = ThreadExecute(self._task_list, self._repeat_count)
            self._thread_execute.sig_terminated.connect(self._on_thread_execute_terminated)
            self._thread_execute.sig_current_task_index.connect(self._on_thread_execute_current_index)
            self._thread_execute.start()
            self.sig_execute_started.emit()

    def _stop_thread_execute(self):
        if self._thread_execute is not None:
            self._thread_execute.stop()

    def _on_thread_execute_terminated(self):
        del self._thread_execute
        self._thread_execute = None
        self.sig_execute_terminated.emit()

    def _on_thread_execute_current_index(self, index: int):
        self.sig_current_executing_task_index.emit(index)

    def to_dict(self) -> dict:
        cfg = {
            "name": self._name,
            "repeat_count": self._repeat_count,
            "task_list": [task.to_dict() for task in self._task_list]
        }
        return cfg

    def from_dict(self, cfg: dict) -> bool:
        self._name = cfg.get("name", "no_named")
        self._repeat_count = cfg.get("repeat_count", 1)
        self._task_list = [load_task_from_dict(x) for x in cfg.get("task_list", [])]
        self.refresh_task(False)
        return True

    def set_file_path(self, file_path: str) -> bool:
        if os.path.isfile(file_path) and os.path.splitext(file_path)[-1].lower() == ".json":
            self._file_path = file_path
        else:
            self._file_path = os.path.join(CFG_PATH, "default_job.json")
        return True

    def save(self):
        try:
            with open(self._file_path, "w") as fp:
                json.dump(self.to_dict(), fp, indent=4)
            GetLogger().info(f"Saved job to file ({self._file_path})", self)
        except Exception as e:
            GetLogger().critical(f"failed to save: {e}", self)

    def save_as(self, file_path: str):
        try:
            with open(file_path, "w") as fp:
                json.dump(self.to_dict(), fp, indent=4)
            GetLogger().info(f"Saved job to file ({file_path})", self)
        except Exception as e:
            GetLogger().critical(f"failed to save: {e}", self)

    def load(self) -> bool:
        try:
            if not os.path.isfile(self._file_path):
                self.save()
            with open(self._file_path, "r") as fp:
                result = self.from_dict(json.load(fp))
            GetLogger().info(f"Loaded job from file ({self._file_path})", self)
            return result
        except Exception as e:
            GetLogger().critical(f"failed to load: {e}", self)
        return False

    def add_task(self, task: Task):
        self._task_list.append(task)
        GetLogger().info(f"Added task {task} at index {self._task_list.index(task)}", self)
        self.refresh_task()

    def remove_task(self, task: Union[int, Task]):
        if isinstance(task, int):
            try:
                task = self._task_list[task]
            except Exception as e:
                GetLogger().critical(f"failed to remove task: {e}", self)
                return
        try:
            idx = self._task_list.index(task)
            self._task_list.remove(task)
            GetLogger().info(f"Removed task at index {idx}", self)
            self.refresh_task()
        except Exception as e:
            GetLogger().critical(f"failed to remove task: {e}", self)

    def clear_task(self):
        self._task_list.clear()
        GetLogger().info(f"Cleared all task(s)", self)
        self.refresh_task()

    def replace_task(self, index: int, new_task: Task):
        try:
            self._task_list[index] = new_task
            GetLogger().info(f"Replaced task at index {index} to {new_task}", self)
            self.refresh_task()
        except Exception as e:
            GetLogger().critical(f"failed to replace task: {e}", self)

    def switch_task(self, index1: int, index2: int):
        try:
            self._task_list[index1], self._task_list[index2] = self._task_list[index2], self._task_list[index1]
            GetLogger().info(f"Switched task index {index1} and index {index2}", self)
            self.refresh_task()
        except Exception as e:
            GetLogger().critical(f"failed to switch task: {e}", self)

    def set_task_name(self, index: int, name: str):
        try:
            self._task_list[index].name = name
            self.refresh_task()
        except Exception as e:
            GetLogger().critical(f"failed to set task name: {e}", self)

    def refresh_task(self, save: bool = True):
        for task in self._task_list:
            task.set_mouse_controller(self._mouse_controller)
            task.set_keyboard_controller(self._keyboard_controller)
        self.sig_task_list_changed.emit()
        if save:
            self.save()

    @property
    def task_list(self) -> List[Task]:
        return self._task_list

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name
        GetLogger().info(f"Changed name as <{self._name}>", self)
        self.save()

    @property
    def repeat_count(self) -> int:
        return self._repeat_count

    @repeat_count.setter
    def repeat_count(self, count: int):
        self._repeat_count = count
        self.save()

    @property
    def file_path(self) -> str:
        return self._file_path
