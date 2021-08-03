from statistics.main import (
    ForbiddenDuplication,
    StatisticCollection,
    TransparentWrapper,
)

import pytest


class TestRecord:
    @staticmethod
    def test_good():
        stats = StatisticCollection()
        stats.record("apple", 12)
        stats.record(("lemon", "apple"), 42)
        stats.record(("lemon", "grape"), 128)

        assert stats["apple"] == 12
        assert stats["lemon"]["apple"] == 42
        assert stats["lemon"]["grape"] == 128

    @staticmethod
    def test_duplication():
        stats = StatisticCollection()
        stats.record("apple", 12)
        stats.record(("lemon", "apple"), 42)

        with pytest.raises(ForbiddenDuplication):
            stats.record("apple", 4)
        with pytest.raises(ForbiddenDuplication):
            stats.record(("apple",), 42)
        with pytest.raises(ForbiddenDuplication):
            stats.record(("lemon", "apple"), 10)
        with pytest.raises(ForbiddenDuplication):
            stats.record(("apple", "green"), 10)


class TestGetItem:
    @staticmethod
    def test_good():
        stats = StatisticCollection()
        stats.record("apple", 12)
        stats.record(("lemon", "apple"), 42)
        stats.record(("lemon", "grape"), 128)

        assert stats["apple"] == 12
        assert stats[("lemon", "apple")] == 42
        assert stats[("lemon", "grape")] == 128

    @staticmethod
    def test_bad():
        stats = StatisticCollection()
        stats.record("apple", 12)
        stats.record(("lemon", "apple"), 42)
        stats.record(("lemon", "grape"), 128)

        with pytest.raises(KeyError):
            _ = stats["dog"]
        with pytest.raises(KeyError):
            _ = stats[("dog",)]
        with pytest.raises(KeyError):
            _ = stats[("apple", "dog")]
        with pytest.raises(KeyError):
            _ = stats[()]


class TestIn:
    @staticmethod
    def test_good():
        stats = StatisticCollection()
        stats.record("apple", 12)
        stats.record(("lemon", "apple"), 42)
        stats.record(("lemon", "grape"), 128)

        assert "apple" in stats
        assert ("lemon", "apple") in stats
        assert ("lemon", "grape") in stats
        assert "dog" not in stats
        assert ("dog",) not in stats
        assert ("lemon", "juice") not in stats

    @staticmethod
    def test_bad():
        stats = StatisticCollection()
        stats.record("apple", 12)
        stats.record(("lemon", "apple"), 42)
        stats.record(("lemon", "grape"), 128)

        with pytest.raises(KeyError):
            _ = ("apple", "dog") in stats
        with pytest.raises(KeyError):
            _ = () in stats


def test_collect():
    stats = StatisticCollection()
    stats.collect("apple", 12)
    stats.collect("apple", -12)

    stats.collect(("lemon", "apple"), 42)
    stats.collect(("lemon", "apple"), -42)

    stats.collect(("lemon", "grape"), 128)
    stats.collect(("lemon", "grape"), -128)

    assert stats["apple"] == [12, -12]
    assert stats[("lemon", "apple")] == [42, -42]
    assert stats[("lemon", "grape")] == [128, -128]


def test_transparent_wrapper():
    stats = StatisticCollection()
    wrapper = TransparentWrapper(stats)

    wrapper.record("apple", 12)
    wrapper.record(("lemon", "apple"), 42)

    assert wrapper["apple"] == 12
    assert wrapper[("lemon", "apple")] == 42


def test_sub_collection():
    stats = StatisticCollection()

    with stats.sub_collection() as sub_collection:
        sub_collection.record("apple", 42)

    assert stats["statistics"]["test_main"]["test_sub_collection"]["apple"] == 42
    assert stats[("statistics", "test_main", "test_sub_collection", "apple")] == 42
