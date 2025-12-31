import os
from PySide6.QtGui import QIcon, QAction


def ensure_path_exist(path: str):
    targetpath = os.path.abspath(path)
    if not os.path.isdir(targetpath):
        if os.name == 'nt':
            pathsplit = targetpath.split('\\')
            ptemp = str(pathsplit[0]) + '\\'
        else:
            pathsplit = targetpath.split('/')
            ptemp = str(pathsplit[0]) + '/'
        for i in range(len(pathsplit) - 1):
            p = pathsplit[i + 1]
            ptemp = os.path.join(ptemp, p)
            ptemp = os.path.abspath(ptemp)
            if not os.path.isdir(ptemp):
                os.mkdir(ptemp)


class MyQAction(QAction):
    _level: int = 0

    def __init__(self, parent, level: int = 0):
        super().__init__(parent=parent)
        self._level = level

    @property
    def level(self):
        return self._level


def make_qaction(**kwargs):
    parent = None
    text = None
    iconPath = None
    triggered = None
    checkable = False
    checked = False
    level = 0

    if 'parent' in kwargs.keys():
        parent = kwargs['parent']
    if 'text' in kwargs.keys():
        text = kwargs['text']
    if 'iconPath' in kwargs.keys():
        iconPath = kwargs['iconPath']
    if 'triggered' in kwargs.keys():
        triggered = kwargs['triggered']
    if 'checkable' in kwargs.keys():
        checkable = kwargs['checkable']
    if 'checked' in kwargs.keys():
        checked = kwargs['checked']
    if 'level' in kwargs.keys():
        level = kwargs['level']

    action = MyQAction(parent, level)
    action.setText(text)
    action.setIcon(QIcon(iconPath))
    if triggered is not None:
        action.triggered.connect(triggered)
    action.setCheckable(checkable)
    action.setChecked(checked)

    return action
