import os
import sys
from typing import List, Union
from threading import Thread
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController
from TaskDefine import (Task, load_task_from_dict)
CUR_PATH = os.path.dirname(os.path.abspath(__file__))  # {PROJ}/Task
PROJ_PATH = os.path.dirname(CUR_PATH)
sys.path.extend([CUR_PATH, PROJ_PATH])
sys.path = list(set(sys.path))
from Util import Callback


class ThreadExecute(Thread):
    def __init__(self, task_list: List[Task], repeat_count: int):
        Thread.__init__(self)
        self.daemon = True
        self._keep_alive: bool = True
        self._task_list = task_list
        self._repeat_count = repeat_count
        self.sig_terminated = Callback()
        self.sig_current_task_index = Callback(int)

    def run(self):
        index: int = 0
        seq_count: int = 0
        print("Started")
        while True:
            if not self._keep_alive:
                break
            try:
                if index < len(self._task_list):
                    task = self._task_list[index]
                    print(f"{task} executing")
                    self.sig_current_task_index.emit(index)
                    task.execute()
                index += 1
                if index >= len(self._task_list):
                    index = 0
                    seq_count += 1
                    if self._repeat_count > 0:
                        if seq_count >= self._repeat_count:
                            break
            except Exception as e:
                print(f"Exception: {e}")
        print("Terminated")
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

    def set_mouse_controller(self, controller: MouseController):
        self._mouse_controller = controller
        self.refresh_task()

    def set_keyboard_controller(self, controller: KeyboardController):
        self._keyboard_controller = controller
        self.refresh_task()

    def execute(self):
        self._start_thread_execute()

    def pause(self):
        pass

    def stop(self):
        self._stop_thread_execute()

    def _start_thread_execute(self):
        if self._thread_execute is None:
            self._thread_execute = ThreadExecute(self._task_list, self._repeat_count)
            self._thread_execute.sig_terminated.connect(self._on_thread_execute_terminated)
            # self._thread_execute.sig_current_task_index.connect()
            self._thread_execute.start()

    def _stop_thread_execute(self):
        if self._thread_execute is not None:
            self._thread_execute.stop()

    def _on_thread_execute_terminated(self):
        del self._thread_execute
        self._thread_execute = None

    def is_executing(self) -> bool:
        return self._thread_execute is not None and self._thread_execute.is_alive()

    def to_dict(self) -> dict:
        cfg = {
            "name": self._name,
            "task_list": [task.to_dict() for task in self._task_list]
        }
        return cfg

    def from_dict(self, cfg: dict):
        self._name = cfg.get("name", "no_named")
        self.clear_task()
        self._task_list = [load_task_from_dict(x) for x in cfg.get("task_list", [])]
        self.refresh_task()

    def save(self, file_path: str):
        pass

    def load(self, file_path: str):
        pass

    def add_task(self, task: Task):
        self._task_list.append(task)
        self.refresh_task()

    def remove_task(self, task: Union[int, Task]):
        if isinstance(task, int):
            try:
                task = self._task_list[task]
            except Exception:
                return
        self._task_list.remove(task)

    def clear_task(self):
        self._task_list.clear()

    def refresh_task(self):
        for task in self._task_list:
            task.set_mouse_controller(self._mouse_controller)
            task.set_keyboard_controller(self._keyboard_controller)


if __name__ == "__main__":
    from TaskDefine import TaskMouseLeftClick, TaskMouseLeftDoubleClick, TaskSleep

    job_ = MacroJob("test")
    job_.set_mouse_controller(MouseController())
    job_.set_keyboard_controller(KeyboardController())
    job_.add_task(TaskMouseLeftClick(300, 300))
    job_.add_task(TaskSleep(1))
    job_.add_task(TaskMouseLeftClick(300, 400))
    job_.add_task(TaskSleep(1))
    job_.add_task(TaskMouseLeftDoubleClick(300, 500))
    job_.add_task(TaskSleep(1))
    job_.execute()
    while job_.is_executing():
        pass
