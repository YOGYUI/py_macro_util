import os
import sys
import time
from enum import IntEnum, unique, auto
from typing import Union
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Key
CUR_PATH = os.path.dirname(os.path.abspath(__file__))  # {PROJ}/Task
PROJ_PATH = os.path.dirname(CUR_PATH)
sys.path.extend([CUR_PATH, PROJ_PATH])
sys.path = list(set(sys.path))
from Util import GetLogger


@unique
class TaskType(IntEnum):
    DEFAULT = 0
    SLEEP = auto()
    MOUSE_MOVE = auto()
    MOUSE_LEFT_CLICK = auto()
    MOUSE_LEFT_DOUBLE_CLICK = auto()
    MOUSE_RIGHT_CLICK = auto()
    MOUSE_RIGHT_DOUBLE_CLICK = auto()
    MOUSE_LEFT_PRESS = auto()
    MOUSE_LEFT_RELEASE = auto()
    MOUSE_RIGHT_PRESS = auto()
    MOUSE_RIGHT_RELEASE = auto()
    MOUSE_SCROLL = auto()
    KEY_PRESS = auto()
    KEY_RELEASE = auto()
    KEY_TYPE = auto()


class Task:
    _mouse_controller: Union[MouseController, None] = None
    _keyboard_controller: Union[KeyboardController, None] = None

    def __init__(self, name: str, task_type: TaskType = TaskType.DEFAULT):
        self._name = name
        self._type = task_type

    def __repr__(self) -> str:
        return f"[{type(self).__name__}({hex(id(self))})]"

    def execute(self) -> bool:
        return True

    def set_mouse_controller(self, controller: MouseController):
        self._mouse_controller = controller

    def set_keyboard_controller(self, controller: KeyboardController):
        self._keyboard_controller = controller

    def to_dict(self) -> dict:
        return {
            "name": self._name,
            "type": self._type.value
        }

    def from_dict(self, cfg: dict):
        self._name = cfg.get("name", self._name)

    @property
    def type(self) -> TaskType:
        return self._type

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name
        GetLogger().info(f"Changed name as <{self._name}>", self)


class TaskSleep(Task):
    def __init__(self, name: str, sleep_time_sec: int = 0):
        super().__init__(name, TaskType.SLEEP)
        self.sleep_time_sec = sleep_time_sec

    def __repr__(self) -> str:
        return f"[{type(self).__name__}({hex(id(self))})] <{self.sleep_time_sec} sec>"

    def execute(self) -> bool:
        GetLogger().info(f"executing <{self.sleep_time_sec} sec>", self)
        time.sleep(self.sleep_time_sec)
        return True

    def to_dict(self) -> dict:
        cfg = super().to_dict()
        cfg["sleep_time_sec"] = self.sleep_time_sec
        return cfg

    def from_dict(self, cfg: dict):
        super().from_dict(cfg)
        self.sleep_time_sec = cfg.get("sleep_time_sec", 0)


class TaskMouseCommon(Task):
    def __init__(self, name: str, task_type: TaskType, pos_x: int = 0, pos_y: int = 0):
        super().__init__(name, task_type)
        self.pos_x = pos_x
        self.pos_y = pos_y

    def __repr__(self) -> str:
        return f"[{type(self).__name__}({hex(id(self))})] <x: {self.pos_x}, y: {self.pos_y}>"

    def to_dict(self) -> dict:
        cfg = super().to_dict()
        cfg["pos_x"] = self.pos_x
        cfg["pos_y"] = self.pos_y
        return cfg

    def from_dict(self, cfg: dict):
        super().from_dict(cfg)
        self.pos_x = cfg.get("pos_x", 0)
        self.pos_y = cfg.get("pos_y", 0)

    def move(self) -> bool:
        if self._mouse_controller is None:
            GetLogger().warning("invalid controller", self)
            return False
        cnt = 0
        while self._mouse_controller.position != (self.pos_x, self.pos_y):
            self._mouse_controller.position = self.pos_x, self.pos_y
            cnt += 1
            if cnt >= 100:
                GetLogger().warning("failed to move point", self)
                return False
        return True


class TaskMouseLeftClick(TaskMouseCommon):
    def __init__(self, name: str, pos_x: int = 0, pos_y: int = 0):
        super().__init__(name, TaskType.MOUSE_LEFT_CLICK, pos_x, pos_y)

    def execute(self) -> bool:
        if self._mouse_controller is None:
            GetLogger().warning("invalid controller", self)
            return False
        try:
            GetLogger().info(f"executing <x: {self.pos_x}, y: {self.pos_y}>", self)
            self.move()
            self._mouse_controller.click(Button.left, 1)
        except Exception as e:
            GetLogger().critical(f"Exception: {e}", self)
            return False
        return True


class TaskMouseRightClick(TaskMouseCommon):
    def __init__(self, name: str, pos_x: int = 0, pos_y: int = 0):
        super().__init__(name, TaskType.MOUSE_RIGHT_CLICK, pos_x, pos_y)

    def execute(self):
        if self._mouse_controller is None:
            GetLogger().warning("invalid controller", self)
            return False
        try:
            GetLogger().info(f"executing <x: {self.pos_x}, y: {self.pos_y}>", self)
            self.move()
            self._mouse_controller.click(Button.right, 1)
        except Exception as e:
            GetLogger().critical(f"Exception: {e}", self)
            return False
        return True


class TaskMouseLeftDoubleClick(TaskMouseCommon):
    def __init__(self, name: str, pos_x: int = 0, pos_y: int = 0):
        super().__init__(name, TaskType.MOUSE_LEFT_DOUBLE_CLICK, pos_x, pos_y)

    def execute(self) -> bool:
        if self._mouse_controller is None:
            GetLogger().warning("invalid controller", self)
            return False
        try:
            GetLogger().info(f"executing <x: {self.pos_x}, y: {self.pos_y}>", self)
            self.move()
            self._mouse_controller.click(Button.left, 2)
        except Exception as e:
            GetLogger().critical(f"Exception: {e}", self)
            return False
        return True


class TaskMouseRightDoubleClick(TaskMouseCommon):
    def __init__(self, name: str, pos_x: int = 0, pos_y: int = 0):
        super().__init__(name, TaskType.MOUSE_RIGHT_DOUBLE_CLICK, pos_x, pos_y)

    def execute(self) -> bool:
        if self._mouse_controller is None:
            GetLogger().warning("invalid controller", self)
            return False
        try:
            GetLogger().info(f"executing <x: {self.pos_x}, y: {self.pos_y}>", self)
            self.move()
            self._mouse_controller.click(Button.right, 2)
        except Exception as e:
            GetLogger().critical(f"Exception: {e}", self)
            return False
        return True


class TaskMouseMove(TaskMouseCommon):
    def __init__(self, name: str, pos_x: int = 0, pos_y: int = 0):
        super().__init__(name, TaskType.MOUSE_MOVE, pos_x, pos_y)

    def execute(self) -> bool:
        GetLogger().info(f"executing <x: {self.pos_x}, y: {self.pos_y}>", self)
        return self.move()


class TaskMouseLeftPress(TaskMouseCommon):
    def __init__(self, name: str, pos_x: int = 0, pos_y: int = 0):
        super().__init__(name, TaskType.MOUSE_LEFT_PRESS, pos_x, pos_y)

    def execute(self) -> bool:
        if self._mouse_controller is None:
            GetLogger().warning("invalid controller", self)
            return False
        try:
            GetLogger().info(f"executing <x: {self.pos_x}, y: {self.pos_y}>", self)
            self.move()
            self._mouse_controller.press(Button.left)
        except Exception as e:
            GetLogger().critical(f"Exception: {e}", self)
            return False
        return True


class TaskMouseLeftRelease(TaskMouseCommon):
    def __init__(self, name: str, pos_x: int = 0, pos_y: int = 0):
        super().__init__(name, TaskType.MOUSE_LEFT_RELEASE, pos_x, pos_y)

    def execute(self) -> bool:
        if self._mouse_controller is None:
            GetLogger().warning("invalid controller", self)
            return False
        try:
            GetLogger().info(f"executing <x: {self.pos_x}, y: {self.pos_y}>", self)
            self.move()
            self._mouse_controller.release(Button.left)
        except Exception as e:
            GetLogger().critical(f"Exception: {e}", self)
            return False
        return True


class TaskMouseRightPress(TaskMouseCommon):
    def __init__(self, name: str, pos_x: int = 0, pos_y: int = 0):
        super().__init__(name, TaskType.MOUSE_RIGHT_PRESS, pos_x, pos_y)

    def execute(self) -> bool:
        if self._mouse_controller is None:
            GetLogger().warning("invalid controller", self)
            return False
        try:
            GetLogger().info(f"executing <x: {self.pos_x}, y: {self.pos_y}>", self)
            self.move()
            self._mouse_controller.press(Button.right)
        except Exception as e:
            GetLogger().critical(f"Exception: {e}", self)
            return False
        return True


class TaskMouseRightRelease(TaskMouseCommon):
    def __init__(self, name: str, pos_x: int = 0, pos_y: int = 0):
        super().__init__(name, TaskType.MOUSE_RIGHT_RELEASE, pos_x, pos_y)

    def execute(self) -> bool:
        if self._mouse_controller is None:
            GetLogger().warning("invalid controller", self)
            return False
        try:
            GetLogger().info(f"executing <x: {self.pos_x}, y: {self.pos_y}>", self)
            self.move()
            self._mouse_controller.release(Button.right)
        except Exception as e:
            GetLogger().critical(f"Exception: {e}", self)
            return False
        return True


class TaskMouseScroll(TaskMouseCommon):
    def __init__(self, name: str, dx: int = 0, dy: int = 0):
        super().__init__(name, TaskType.MOUSE_SCROLL, 0, 0)
        self.dx = dx
        self.dy = dy

    def __repr__(self) -> str:
        return f"[{type(self).__name__}({hex(id(self))})] <dx: {self.dx}, dy: {self.dy}>"

    def to_dict(self) -> dict:
        cfg = super().to_dict()
        cfg["dx"] = self.dx
        cfg["dy"] = self.dy
        return cfg

    def from_dict(self, cfg: dict):
        super().from_dict(cfg)
        self.dx = cfg.get("dx", 0)
        self.dy = cfg.get("dy", 0)

    def execute(self) -> bool:
        if self._mouse_controller is None:
            GetLogger().warning("invalid controller", self)
            return False
        try:
            GetLogger().info(f"executing <x: {self.dx}, y: {self.dy}>", self)
            self._mouse_controller.scroll(self.dx, self.dy)
        except Exception as e:
            GetLogger().critical(f"Exception: {e}", self)
            return False
        return True


class TaskKeyPress(Task):
    def __init__(self, name: str):
        super().__init__(name, TaskType.KEY_PRESS)
        # self.key = Key.
        pass

    def execute(self) -> bool:
        GetLogger().info("executing <>", self)
        self._keyboard_controller.press(self.key)
        return True

    def to_dict(self) -> dict:
        cfg = super().to_dict()
        return cfg

    def from_dict(self, cfg: dict):
        super().from_dict(cfg)


class TaskKeyRelease(Task):
    def __init__(self, name: str):
        super().__init__(name, TaskType.KEY_RELEASE)

    def execute(self) -> bool:
        GetLogger().info("executing <>", self)
        # self._keyboard_controller.press(Key)
        return True

    def to_dict(self) -> dict:
        cfg = super().to_dict()
        return cfg

    def from_dict(self, cfg: dict):
        super().from_dict(cfg)


class TaskKeyType(Task):
    def __init__(self, name: str):
        super().__init__(name, TaskType.KEY_TYPE)
        self.string = "string to type in"

    def execute(self) -> bool:
        GetLogger().info("executing <>", self)
        self._keyboard_controller.type(self.string)
        return True

    def to_dict(self) -> dict:
        cfg = super().to_dict()
        cfg["string"] = self.string
        return cfg

    def from_dict(self, cfg: dict):
        super().from_dict(cfg)
        self.string = cfg.get("string", "string to type in")



def load_task_from_dict(cfg: dict) -> Task:
    task = Task("no_named", TaskType.DEFAULT)
    try:
        task_type = TaskType(cfg.get("type", 0))
    except Exception as e:
        GetLogger().critical(f"exception while loading task from dict: {e}")
        return task

    if task_type == TaskType.SLEEP:
        task = TaskSleep("delay")
    elif task_type == TaskType.MOUSE_LEFT_CLICK:
        task = TaskMouseLeftClick("left click")
    elif task_type == TaskType.MOUSE_RIGHT_CLICK:
        task = TaskMouseRightClick("right click")
    elif task_type == TaskType.MOUSE_LEFT_DOUBLE_CLICK:
        task = TaskMouseLeftDoubleClick("left double click")
    elif task_type == TaskType.MOUSE_RIGHT_DOUBLE_CLICK:
        task = TaskMouseRightDoubleClick("right double click")
    elif task_type == TaskType.MOUSE_MOVE:
        task = TaskMouseMove("move")
    elif task_type == TaskType.MOUSE_LEFT_PRESS:
        task = TaskMouseLeftPress("left press")
    elif task_type == TaskType.MOUSE_LEFT_RELEASE:
        task = TaskMouseLeftRelease("left release")
    elif task_type == TaskType.MOUSE_RIGHT_PRESS:
        task = TaskMouseRightPress("right press")
    elif task_type == TaskType.MOUSE_RIGHT_RELEASE:
        task = TaskMouseRightRelease("right release")
    elif task_type == TaskType.MOUSE_SCROLL:
        task = TaskMouseScroll("scroll")
    elif task_type == TaskType.KEY_PRESS:
        task = TaskKeyPress("key press")
    elif task_type == TaskType.KEY_RELEASE:
        task = TaskKeyRelease("key release")
    elif task_type == TaskType.KEY_TYPE:
        task = TaskKeyType("key type")
    task.from_dict(cfg)
    return task


def create_task(task_type: TaskType) -> Task:
    return load_task_from_dict({"type": task_type.value})
