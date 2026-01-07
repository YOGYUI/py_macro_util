import os
import sys
import time
import copy
from enum import IntEnum, unique, auto
from typing import Union, List
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import KeyCode, Key
CUR_PATH = os.path.dirname(os.path.abspath(__file__))  # {PROJ}/Include/Task
INC_PATH = os.path.dirname(CUR_PATH)
PROJ_PATH = os.path.dirname(INC_PATH)
UTIL_PATH = os.path.join(INC_PATH, "Util")
sys.path.extend([CUR_PATH, INC_PATH, UTIL_PATH, PROJ_PATH])
sys.path = list(set(sys.path))
from Logger import GetLogger


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
    KEYBOARD_SEQUENCE = auto()
    KEYBOARD_STRING = auto()


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


@unique
class KeyTaskType(IntEnum):
    PRESS = auto()
    RELEASE = auto()


class KeyTask:
    _controller: Union[KeyboardController, None] = None

    def __init__(self, key: Union[Key, KeyCode], task_type: KeyTaskType):
        self._key = key
        self._task_type = task_type

    def __repr__(self) -> str:
        return f"[{type(self).__name__}({hex(id(self))})] <{self._task_type.name[0]}><{self._key}>"

    def execute(self):
        if self._task_type == KeyTaskType.PRESS:
            self._controller.press(self._key)
        elif self._task_type == KeyTaskType.RELEASE:
            self._controller.release(self._key)

    def set_controller(self, controller: KeyboardController):
        self._controller = controller

    def to_string(self) -> str:
        res = f"[{self._task_type.name[0]}]"
        if isinstance(self._key, Key):
            res += f"{self._key.name}"
        elif isinstance(self._key, KeyCode):
            res += f"{self._key.char}"
        return res

    def to_tuple(self) -> tuple:
        value = None
        if isinstance(self._key, Key):
            value = self._key.name
        elif isinstance(self._key, KeyCode):
            value = self._key.vk
        return self._task_type.value, value

    def is_same(self, key: Union[Key, KeyCode], task_type: KeyTaskType) -> bool:
        if self._task_type == task_type:
            if type(key) == type(self._key):
                if isinstance(key, Key):
                    return self._key.name == key.name
                elif isinstance(key, KeyCode):
                    return self._key.vk == key.vk
        return False

    @property
    def key(self) -> KeyCode:
        return self._key


class TaskKeyboardSequence(Task):
    def __init__(self, name: str):
        super().__init__(name, TaskType.KEYBOARD_SEQUENCE)
        self._sequence: List[KeyTask] = list()
        self._temp_sequence: List[KeyTask] = list()
        self.interval_msec: float = 1.0

    def execute(self) -> bool:
        GetLogger().info("executing", self)
        for seq in self._sequence:
            seq.execute()
            time.sleep(self.interval_msec / 1000)
        return True

    def to_dict(self) -> dict:
        cfg = super().to_dict()
        cfg["sequence"] = [seq.to_tuple() for seq in self._sequence]
        return cfg

    def from_dict(self, cfg: dict):
        super().from_dict(cfg)
        self._sequence.clear()
        sequence_list = cfg.get("sequence", [])
        for elem in sequence_list:
            seq_type, seq_value = elem
            key = None
            if isinstance(seq_value, str):
                key = Key[seq_value]
            elif isinstance(seq_value, int):
                key = KeyCode.from_vk(seq_value)
            task = KeyTask(key, KeyTaskType(seq_type))
            self._sequence.append(task)

    def to_string(self) -> str:
        return ', '.join([seq.to_string() for seq in self._sequence])

    def add_sequence_press(self, key: Union[Key, KeyCode]):
        # 중복 입력 방지
        if len(self._sequence) > 0:
            prev_seq = self._sequence[-1]
            if prev_seq.is_same(key, KeyTaskType.PRESS):
                return
        task = KeyTask(key, KeyTaskType.PRESS)
        self._sequence.append(task)
        self.refresh()

    def add_sequence_release(self, key: Union[Key, KeyCode]):
        # 중복 입력 방지
        if len(self._sequence) > 0:
            prev_seq = self._sequence[-1]
            if prev_seq.is_same(key, KeyTaskType.RELEASE):
                return
        task = KeyTask(key, KeyTaskType.RELEASE)
        self._sequence.append(task)
        self.refresh()

    def set_sequence(self, seq: List[KeyTask]):
        self._sequence = seq

    def clear_sequence(self):
        self._temp_sequence = copy.copy(self._sequence)
        self._sequence.clear()

    def recover_sequence(self):
        self._sequence = copy.copy(self._temp_sequence)
        self._temp_sequence.clear()

    def set_keyboard_controller(self, controller: KeyboardController):
        self._keyboard_controller = controller
        self.refresh()

    def refresh(self):
        for seq in self._sequence:
            seq.set_controller(self._keyboard_controller)

    @property
    def sequence(self) -> List[KeyTask]:
        return self._sequence


class TaskKeyboardString(Task):
    def __init__(self, name: str):
        super().__init__(name, TaskType.KEYBOARD_STRING)
        self.string: str = "string to type"

    def execute(self) -> bool:
        GetLogger().info("executing", self)
        self._keyboard_controller.type(self.string)
        return True

    def to_dict(self) -> dict:
        cfg = super().to_dict()
        cfg["string"] = self.string
        return cfg

    def from_dict(self, cfg: dict):
        super().from_dict(cfg)
        self.string = cfg.get("string", "string to type")


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
    elif task_type == TaskType.KEYBOARD_SEQUENCE:
        task = TaskKeyboardSequence("keyboard sequence")
    elif task_type == TaskType.KEYBOARD_STRING:
        task = TaskKeyboardString("keyboard string")
    task.from_dict(cfg)
    return task


def create_task(task_type: TaskType) -> Task:
    return load_task_from_dict({"type": task_type.value})
