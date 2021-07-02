import inspect
import logging

import log.config


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
            "[%(levelname)s FROM %(name)s] %(message)s\n"
            "\tIN %(funcName)s (%(filename)s:%(lineno)d)"
            "\tAT %(asctime)s",
            "%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)
    return logger
