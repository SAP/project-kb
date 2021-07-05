import inspect
import logging
from pprint import pformat

import log.config


def pretty_log(self: logging.Logger, obj, level: int = logging.DEBUG):
    as_text = pformat(obj)
    self.log(level, "detailed content of the object\n" + as_text)


def init_local_logger():
    previous_frame = inspect.currentframe().f_back
    logger_name = "main"
    if previous_frame:
        logger_name = inspect.getmodule(previous_frame).__name__
    logger = logging.getLogger(logger_name)
    logger.setLevel(log.config.level)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "[%(levelname)s FROM %(name)s] %(message)s"
            "\n\tIN %(funcName)s (%(filename)s:%(lineno)d)"
            "\n\tAT %(asctime)s",
            "%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)

    setattr(logging.Logger, pretty_log.__name__, pretty_log)

    return logger
