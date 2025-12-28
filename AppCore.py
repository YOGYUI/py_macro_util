import os
import sys
from threading import Thread
from pynput.mouse import Controller as MouseController
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Listener as KeyboardListener
from Task import *
from Util import Logger, Callback, ensure_path_exist
PROJ_PATH = os.path.dirname(os.path.abspath(__file__))
CFG_PATH = os.path.join(PROJ_PATH, "Config")


class ThreadMonitor(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        pass

    def stop(self):
        pass


class AppCore:
    def __init__(self):
        super().__init__()
        self._job = MacroJob("")
        self._job.set_mouse_controller(MouseController())
        self._job.set_keyboard_controller(KeyboardController())

    def release(self):
        pass
