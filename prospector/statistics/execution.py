import inspect
import time
from statistics.main import StatisticCollection
from typing import Optional, Tuple, Union

execution_statistics = StatisticCollection()


class TimerError(Exception):
    ...


class Timer:
    def __init__(self):
        self._start_time = None

    def start(self):
        if self._start_time is not None:
            raise TimerError("Timer is running. Use .stop() to stop it")
        self._start_time = time.perf_counter()

    def stop(self):
        if self._start_time is None:
            raise TimerError("Timer is not running. Use .start() to start it")

        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        return elapsed_time


def measure_execution_time(name: Optional[Union[str, Tuple[str, ...]]] = None):
    def _measure(function):
        nonlocal name
        if name is None:
            name = tuple(function.__module__.split(".") + function.__name__.split("."))

        def _wrapper(*args, **kwargs):
            timer = Timer()
            timer.start()
            result = function(*args, **kwargs)
            elapsed = timer.stop()
            execution_statistics.collect(name, elapsed)
            return result

        return _wrapper

    return _measure


class execution_timer:
    def __init__(self, name: Union[str, Tuple[str, ...]]):
        self.timer = Timer()
        self.name = name

    def __enter__(self):
        self.timer.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_statistics.collect(self.name, self.timer.stop())
        if exc_val:
            raise exc_val


class counter:
    def __init__(self, parent_name: Optional[Union[str, Tuple[str, ...]]] = None):
        if parent_name is None:
            previous_frame = inspect.currentframe().f_back
            parent_name = "main"
            if previous_frame:
                parent_name = inspect.getmodule(previous_frame).__name__

        self.parent_name = parent_name
        if self.parent_name not in execution_statistics:
            execution_statistics.record(self.parent_name, StatisticCollection())

    def __enter__(self) -> StatisticCollection:
        return execution_statistics[self.parent_name]

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            raise exc_val
