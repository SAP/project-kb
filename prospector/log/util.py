import inspect
import logging
import logging.handlers
from pprint import pformat

import log.config


def pretty_log(self: logging.Logger, obj, level: int = logging.DEBUG):
    as_text = pformat(obj)
    self.log(level, "detailed content of the object\n" + as_text)


def init_local_logger():
    previous_frame = inspect.currentframe().f_back
    logger_name = "main"
    try:
        if previous_frame:
            logger_name = inspect.getmodule(previous_frame).__name__
    except Exception:
        print(f"error during logger name determination, using '{logger_name}'")
    logger = logging.getLogger(logger_name)
    logger.setLevel(log.config.level)
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
    logger.addHandler(error_file)

    all_file = logging.handlers.TimedRotatingFileHandler(
        "all.log", when="h", backupCount=5
    )
    all_file.setLevel(logging.DEBUG)
    all_file.setFormatter(detailed_formatter)
    logger.addHandler(all_file)

    setattr(logging.Logger, pretty_log.__name__, pretty_log)

    return logger
