import logging
import logging.handlers
from pprint import pformat

LOGGER_NAME = "main"


def pretty_log(logger: logging.Logger, obj, level: int = logging.DEBUG):
    as_text = pformat(obj)
    logger.log(level, f"Object content: {as_text}")


def get_level(string: bool = False):
    global logger
    if string:
        return logging.getLevelName(logger.level)

    return logger.level


def create_logger(
    log_file: str = "prospector.log", name: str = LOGGER_NAME
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s",
        "%m-%d %H:%M:%S",
    )
    log_file = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=2 * (10**6), backupCount=3
    )
    log_file.setFormatter(formatter)
    logger.addHandler(log_file)

    setattr(logger, pretty_log.__name__, pretty_log)

    return logger


logger = create_logger()
