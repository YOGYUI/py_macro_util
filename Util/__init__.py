import os
import sys
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([CUR_PATH])
sys.path = list(set(sys.path))

from Callback import Callback
from ErrorHandler import ErrorHandler
