import time

import pytest

from stats.collection import StatisticCollection
from stats.execution import Counter, ExecutionTimer, measure_execution_time


class TestMeasureTime:
    @staticmethod
    @pytest.mark.skip(reason="Not implemented yet")
    def test_decorator():
        stats = StatisticCollection()

        @measure_execution_time(stats)
        def _dummy(laziness: int) -> int:
            time.sleep(laziness)
            return laziness

        _dummy(1)
        _dummy(2)

        assert (
            len(
                stats[
                    (
                        "stats",
                        "test_execution",
                        "TestMeasureTime",
                        "test_decorator",
                        "<locals>",
                        "_dummy",
                        "execution time",
                    )
                ]
            )
            == 2
        )
        assert (
            1
            < stats[
                (
                    "stats",
                    "test_execution",
                    "TestMeasureTime",
                    "test_decorator",
                    "<locals>",
                    "_dummy",
                    "execution time",
                )
            ][0]
            < 1.1
        )
        assert (
            2
            < stats[
                (
                    "stats",
                    "test_execution",
                    "TestMeasureTime",
                    "test_decorator",
                    "<locals>",
                    "_dummy",
                    "execution time",
                )
            ][1]
            < 2.1
        )

    @staticmethod
    def test_manual():
        stats = StatisticCollection()
        timer = ExecutionTimer(stats)
        for i in range(10):
            timer.start()
            time.sleep(i / 10)
            timer.stop()

        assert len(stats["execution time"]) == 10
        for i in range(10):
            assert i / 10 < stats["execution time"][i] < i / 10 + 0.1

    @staticmethod
    @pytest.mark.skip(reason="Not implemented yet")
    def test_with():
        stats = StatisticCollection()
        for i in range(10):
            with ExecutionTimer(stats.sub_collection()):
                time.sleep(i / 10)

        assert (
            len(stats["stats"]["test_execution"]["test_with"]["execution time"]) == 10
        )
        for i, measured_time in enumerate(
            stats["stats"]["test_execution"]["test_with"]["execution time"]
        ):
            assert i / 10 < measured_time < i / 10 + 0.1


class TestCounter:
    @staticmethod
    def test_initialize():
        counter = Counter(StatisticCollection())
        counter.initialize("kiwi", "grape")
        counter.initialize("apple", "lemon", value=42)

        assert counter.collection["kiwi"] == [0]
        assert counter.collection["grape"] == [0]

        assert counter.collection["apple"] == [42]
        assert counter.collection["lemon"] == [42]

    @staticmethod
    def test_manual():
        counter = Counter(StatisticCollection())
        counter.collection.record("apple", 12)
        counter.collection.record("lemon", [1, 2, 3, 4])

        with pytest.raises(KeyError):
            counter.increment("apricot")

        counter.increment("apple")
        assert counter.collection["apple"] == 13

        counter.increment("apple", 3)
        assert counter.collection["apple"] == 16

        counter.increment("lemon")
        assert counter.collection["lemon"] == [1, 2, 3, 5]

        counter.increment("lemon", 3)
        assert counter.collection["lemon"] == [1, 2, 3, 8]

    @staticmethod
    def test_with():
        stats = StatisticCollection()
        with Counter(stats.sub_collection()) as counter:
            counter.collection.record("apple", 12)
            counter.collection.record("lemon", [1, 2, 3, 4])

            with pytest.raises(KeyError):
                counter.increment("apricot")

            counter.increment("apple")
            assert counter.collection["apple"] == 13

            counter.increment("apple", 3)
            assert counter.collection["apple"] == 16

            counter.increment("lemon")
            assert counter.collection["lemon"] == [1, 2, 3, 5]

            counter.increment("lemon", 3)
            assert counter.collection["lemon"] == [1, 2, 3, 8]
