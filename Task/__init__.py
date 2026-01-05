import os
import sys
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([CUR_PATH])
sys.path = list(set(sys.path))

from JobDefine import MacroJob
from TaskDefine import (Task, TaskType, load_task_from_dict, create_task, TaskSleep)
from TaskDefine import (TaskMouseCommon, TaskMouseMove, TaskMouseLeftClick, TaskMouseRightClick,
                        TaskMouseLeftDoubleClick, TaskMouseRightDoubleClick,
                        TaskMouseLeftPress, TaskMouseLeftRelease,
                        TaskMouseRightPress, TaskMouseRightRelease,
                        TaskMouseScroll)
from TaskDefine import (TaskKeySequence)
