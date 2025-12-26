from typing import List
from TaskDefine import *


class MacroJob:
    def __init__(self):
        self._task_list: List[TaskCommon] = list()

    def execute(self):
        pass

    def to_dict(self) -> dict:
        return {}

    def from_dict(self, cfg: dict):
        pass

    def save(self, file_path: str):
        pass

    def load(self, file_path: str):
        pass
