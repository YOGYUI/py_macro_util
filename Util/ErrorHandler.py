import os
import socket
import logging
import logging.handlers
import platform
import traceback
from Functions import ensure_path_exist
CUR_PATH = os.path.dirname(os.path.abspath(__file__))  # {PROJ}/Util
PROJ_PATH = os.path.dirname(CUR_PATH)
MAX_SIZE = 100 * 1024 * 1024


class ErrorHandler:
    _logger = None
    _logFilePath = ""

    def __init__(self):
        filePath = os.path.join(PROJ_PATH, 'Log/Error.log')
        self._logFilePath = filePath
        ensure_path_exist(os.path.dirname(filePath))

        self._logger = logging.getLogger('error')
        fh = logging.handlers.RotatingFileHandler(filePath, maxBytes=MAX_SIZE, backupCount=10, encoding='utf-8')

        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
        fh.setFormatter(formatter)

        self._logger.addHandler(fh)
        self._logger.setLevel(logging.DEBUG)

        hostname = socket.gethostname()
        self._logger.info('Host: ' + hostname)
        self._logger.info('Address: ' + socket.gethostbyname(hostname))

    def report(self):
        traceback.print_exc()
        self._logger.error(traceback.format_exc())

        x = list(self._logger.handlers)
        for i in x:
            self._logger.removeHandler(i)
            i.flush()
            i.close()
        self.openLogFile()

    def openLogFile(self):
        if platform.system() == 'Windows':
            os.startfile(self._logFilePath)

    @property
    def logFilePath(self) -> str:
        return self._logFilePath
