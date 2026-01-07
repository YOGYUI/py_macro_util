import os
import sys
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([CUR_PATH])
sys.path = list(set(sys.path))

from JobManagerWidget import JobManagerWidget
from AboutWidget import AboutWindow
from UpdateWidget import UpdateWindow

__all__ = ["JobManagerWidget", "AboutWindow", "UpdateWindow"]