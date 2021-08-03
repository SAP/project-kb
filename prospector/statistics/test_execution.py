import time
from statistics.execution import (
    execution_statistics,
    execution_timer,
    measure_execution_time,
)


def test_measure_execution_time():
    @measure_execution_time()
    def _dummy(laziness: int) -> int:
        time.sleep(laziness)
        return laziness

    _dummy(1)
    _dummy(2)

    assert len(execution_statistics["statistics"]["test_execution"]["_dummy"]) == 2
    assert 1 < execution_statistics["statistics"]["test_execution"]["_dummy"][0] < 1.1
    assert 2 < execution_statistics["statistics"]["test_execution"]["_dummy"][1] < 2.1


def test_execution_timer():
    for i in range(10):
        with execution_timer("test"):
            time.sleep(i / 10)

    assert len(execution_statistics["test"]) == 10
    for i in range(10):
        assert i / 10 < execution_statistics["test"][i] < i / 10 + 0.1


def test_counter():
    ...
