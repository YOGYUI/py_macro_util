import time
from enum import IntEnum, unique, auto
from typing import Union
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Key


@unique
class TaskType(IntEnum):
    DEFAULT = auto()
    SLEEP = auto()
    MOUSE_LEFT_CLICK = auto()
    MOUSE_RIGHT_CLICK = auto()
    MOUSE_LEFT_DOUBLE_CLICK = auto()
    MOUSE_RIGHT_DOUBLE_CLICK = auto()
    MOUSE_MODE = auto()


class TaskCommon:
    _mouse_controller: Union[MouseController, None] = None
    _keyboard_controller: Union[KeyboardController, None] = None

    def __init__(self, task_type: TaskType):
        self._type = task_type

    def execute(self):
        pass

    def set_mouse_controller(self, controller: MouseController):
        self._mouse_controller = controller

    def set_keyboard_controller(self, controller: KeyboardController):
        self._keyboard_controller = controller

    def to_dict(self) -> dict:
        return {"type": self._type.value}

    def from_dict(self, cfg: dict):
        pass


class TaskSleep(TaskCommon):
    def __init__(self):
        super().__init__(TaskType.SLEEP)

    def execute(self):
        pass


class TaskMouseLeftClick(TaskCommon):
    def __init__(self, pos_x: int, pos_y: int, count: int):
        super().__init__(TaskType.MOUSE_LEFT_CLICK)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.count = count

    def execute(self):
        ctrl = MouseController()
        ctrl.position = (self.pos_x, self.pos_x)
        ctrl.click(Button.left, self.count)

    def to_dict(self) -> dict:
        obj = super().to_dict()
        obj["pos_x"] = self.pos_x
        obj["pos_y"] = self.pos_y
        obj["count"] = self.count
        return obj

    def from_dict(self, cfg: dict):
        pass


class TaskMouseRightClick(TaskCommon):
    def execute(self):
        pass


class TaskMouseLeftDoubleClick(TaskCommon):
    def execute(self):
        pass


class TaskMouseRightDoubleClick(TaskCommon):
    def execute(self):
        pass


class TaskMouseMove(TaskCommon):
    def execute(self):
        pass
