from __future__ import annotations

import time
from typing import Optional, Tuple, Union

from stats.collection import StatisticCollection, SubCollectionWrapper

# Global execution  statistics to store all data in
execution_statistics = StatisticCollection()


def set_new():
    global execution_statistics
    execution_statistics = StatisticCollection()


class TimerError(Exception):
    ...


class Timer:
    """A simple timer to measure elapsed time."""

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


def measure_execution_time(
    collection: StatisticCollection,
    name: Optional[Union[str, Tuple[str, ...]]] = None,
):
    """A function decorator that measures and records the execution time of the
    decorated function.
    """

    def _measure(function):
        nonlocal name
        if name is None:
            name = tuple(
                function.__module__.split(".") + function.__qualname__.split(".")
            )

        def _wrapper(*args, **kwargs):
            with ExecutionTimer(collection.sub_collection(name)):
                result = function(*args, **kwargs)
            return result

        return _wrapper

    return _measure


class ExecutionTimer(SubCollectionWrapper):
    """Allows measuring time within the context of a `StatisticCollection`."""

    def __init__(self, collection, name: Optional[Union[str, Tuple[str, ...]]] = None):
        super().__init__(collection)
        self.timer = Timer()
        if name is None:
            self.name = "execution time"

    def start(self):
        self.timer.start()

    def stop(self):
        self.collection.collect(self.name, self.timer.stop(), unit="seconds")

    def __enter__(self) -> ExecutionTimer:
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        if exc_val:
            raise exc_val


class Counter(SubCollectionWrapper):
    """Allows incrementing counts within the context of a `StatisticCollection`."""

    def __enter__(self) -> Counter:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            raise exc_val

    def increment(self, name: Union[str, Tuple[str, ...]], by: Union[int, float] = 1):
        selected = self.collection[name]
        if isinstance(selected, list) and (
            isinstance(selected[-1], int) or isinstance(selected[-1], float)
        ):
            selected[-1] += by
        elif isinstance(selected, int) or isinstance(selected, float):
            self.collection.record(name, selected + by, overwrite=True)
        else:
            ValueError(f"can not increment {name}")

    def initialize(
        self,
        *keys: Union[str, Tuple[str, ...]],
        value=0,
        unit: Optional[str] = None,
    ):
        for key in keys:
            self.collection.collect(key, value, unit=unit)
