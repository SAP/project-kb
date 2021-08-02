from statistics.main import ForbiddenDuplication, StatisticCollection

import pytest


class TestRecord:
    @staticmethod
    def test_good():
        stats = StatisticCollection()
        stats.record("apple", 12)
        stats.record(("lemon", "apple"), 42)

        assert stats["apple"] == 12
        assert stats["lemon"]["apple"] == 42

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
