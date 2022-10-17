# from asyncio.log import _logger
from ctypes import Union
import inspect
import logging
import logging.handlers
from pprint import pformat
from typing import Tuple

LOGGER_NAME = "main"


class CLogger:
    def __init__(self, name: str = None):
        if name:
            self._logger = logging.getLogger(name)
        else:
            self._logger = logging.getLogger(LOGGER_NAME)

        self._logger.setLevel(logging.INFO)
        detailed_formatter = logging.Formatter(
            "%(message)s"
            "\n\tOF %(levelname)s FROM %(name)s"
            "\n\tIN %(funcName)s (%(filename)s:%(lineno)d)"
            "\n\tAT %(asctime)s",
            "%Y-%m-%d %H:%M:%S",
        )
        error_file = logging.handlers.TimedRotatingFileHandler(
            "error.log", when="h", backupCount=5
        )
        error_file.setLevel(logging.ERROR)
        error_file.setFormatter(detailed_formatter)
        self._logger.addHandler(error_file)

        all_file = logging.handlers.TimedRotatingFileHandler(
            "all.log", when="h", backupCount=5
        )
        all_file.setLevel(logging.DEBUG)
        all_file.setFormatter(detailed_formatter)
        self._logger.addHandler(all_file)

        setattr(self._logger, self.pretty_log.__name__, self.pretty_log)

    def pretty_log(self, obj, level: int = logging.DEBUG):
        as_text = pformat(obj)
        self._logger.log(level, "detailed content of the object\n" + as_text)

    def get_level(self, string: bool = False):
        if string:
            return logging.getLevelName(self._logger.level)

        return self._logger.level

    def set_level(self, level):
        self._logger.setLevel(level)

    def log(self, level: int, msg: str, *args, **kwargs):
        self._logger.log(level, msg, *args, **kwargs)

    def debug(self, msg: str, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self._logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs):
        self._logger.exception(msg, *args, **kwargs)

    def fatal(self, msg: str, *args, **kwargs):
        self._logger.fatal(msg, *args, **kwargs)


logger = CLogger()


# def init_local__logger():
#     previous_frame = inspect.currentframe().f_back
#     _logger_name = "main"
#     try:
#         if previous_frame:
#             _logger_name = inspect.getmodule(previous_frame).__name__
#     except Exception:
#         print(f"error during _logger name determination, using '{_logger_name}'")
#     _logger = logging.getLogger(_logger_name)
#     _logger.setLevel(level)
#     detailed_formatter = logging.Formatter(
#         "%(message)s"
#         "\n\tOF %(levelname)s FROM %(name)s"
#         "\n\tIN %(funcName)s (%(filename)s:%(lineno)d)"
#         "\n\tAT %(asctime)s",
#         "%Y-%m-%d %H:%M:%S",
#     )

#     error_file = logging.handlers.TimedRotatingFileHandler(
#         "error.log", when="h", backupCount=5
#     )
#     error_file.setLevel(logging.ERROR)
#     error_file.setFormatter(detailed_formatter)
#     _logger.addHandler(error_file)

#     all_file = logging.handlers.TimedRotatingFileHandler(
#         "all.log", when="h", backupCount=5
#     )
#     all_file.setLevel(logging.DEBUG)
#     all_file.setFormatter(detailed_formatter)
#     _logger.addHandler(all_file)

#     setattr(logging.Logger, pretty_log.__name__, pretty_log)

#     return _logger
