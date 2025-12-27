from PySide6.QtCore import QObject
from Task import *
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController


class AppCore(QObject):
    def __init__(self):
        super().__init__()
        self._job = MacroJob("empty job", self)
