# todo: file writting (error, critical)
import logging
from typing import Union


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "[%(asctime)s] [%(levelname)s] %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Logger:
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, name="logger"):
        self._logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        handler.setFormatter(CustomFormatter())
        self._logger.addHandler(handler)
        self._logger.setLevel(logging.DEBUG)

    @staticmethod
    def _make_message(msg: str, obj: object = None) -> str:
        if obj is not None:
            msg = f"[{type(obj).__name__}({hex(id(obj))})] " + msg
        return msg

    def debug(self, msg: str, obj: object = None):
        self._logger.debug(self._make_message(msg, obj))

    def info(self, msg: str, obj: object = None):
        self._logger.info(self._make_message(msg, obj))

    def warning(self, msg: str, obj: object = None):
        self._logger.warning(self._make_message(msg, obj))

    def error(self, msg: str, obj: object = None):
        self._logger.error(self._make_message(msg, obj))

    def critical(self, msg: str, obj: object = None):
        self._logger.critical(self._make_message(msg, obj))


g_logger: Union[Logger, None] = None


def GetLogger() -> Logger:
    global g_logger
    if g_logger is None:
        g_logger = Logger()
    return g_logger
