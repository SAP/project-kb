from log.logger import logger


class Singleton(type):
    """Singleton class to ensure that any class inheriting from this one can only be instantiated once."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            logger.info(
                f"Cannot instantiate a Singleton twice. Returning already existing instance of class {cls}."
            )
        return cls._instances[cls]
