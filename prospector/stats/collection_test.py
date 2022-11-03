import pytest

from stats.collection import (
    ForbiddenDuplication,
    StatisticCollection,
    TransparentWrapper,
)


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


@pytest.mark.skip(reason="Not implemented yet")
def test_sub_collection():
    stats = StatisticCollection()

    with stats.sub_collection() as sub_collection:
        sub_collection.record("apple", 42)

    assert stats["stats"]["test_collection"]["test_sub_collection"]["apple"] == 42
    assert (
        stats[
            (
                "stats",
                "test_collection",
                "test_sub_collection",
                "apple",
            )
        ]
        == 42
    )


def test_descant():
    stats = StatisticCollection()
    stats.record("apple", 12)
    stats.record("grape", 84)
    stats.record(("lemon", "apple"), 42, unit="globe")
    stats.record(("lemon", "grape"), 128)

    descants = stats.get_descants()
    descants_list = list(descants)

    assert (("apple",), 12, None) in descants_list
    assert (("grape",), 84, None) in descants_list
    assert (("lemon",), stats["lemon"], None) in descants_list
    assert (("lemon", "apple"), 42, "globe") in descants_list
    assert (
        (
            "lemon",
            "grape",
        ),
        128,
        None,
    ) in descants_list


def test_console_tree():
    stats = StatisticCollection()
    stats.record("apple", 12)
    stats.record("grape", 84)
    stats.record(("lemon", "apple"), 42, unit="cochren")
    stats.record(("lemon", "grape"), 128, unit="pezeta")
    stats.collect(("lemon", "zest"), 1)
    stats.collect(("lemon", "zest"), 3)
    stats.collect(("lemon", "zest"), 12)
    stats.collect(("lemon", "zest"), 56)
    stats.collect(("melon", "marry"), 34)
    stats.collect(("melon", "marry"), 34.12)
    stats.collect(("melon", "sweet"), 27)
    stats.collect(("melon", "sweet"), 27.23)
    stats.collect(("melon", "sweet"), 0.27)
    stats.collect(("melon", "sweet"), 2.3)

    tree = stats.generate_console_tree()
    assert tree == (
        "+--+[root]\n"
        "|  +---[apple] = 12\n"
        "|  +---[grape] = 84\n"
        "|  +--+[lemon]\n"
        "|  |  +---[apple] = 42 cochren\n"
        "|  |  +---[grape] = 128 pezeta\n"
        "|  |  +---[zest] is a list of numbers with\n"
        "|  |             average = 18\n"
        "|  |             deviation = 25.78113005022601\n"
        "|  |             median = 7.5\n"
        "|  |             count = 4\n"
        "|  |             sum = 72\n"
        "|  +--+[melon]\n"
        "|  |  +---[marry] is a list of numbers with\n"
        "|  |              average = 34.06\n"
        "|  |              deviation = 0.08485281374238389\n"
        "|  |              median = 34.06\n"
        "|  |              count = 2\n"
        "|  |              sum = 68.12\n"
        "|  |  +---[sweet] is a list of numbers with\n"
        "|  |              average = 14.2\n"
        "|  |              deviation = 14.936262361559312\n"
        "|  |              median = 14.65\n"
        "|  |              count = 4\n"
        "|  |              sum = 56.800000000000004"
    )


def test_html_ul():
    stats = StatisticCollection()
    stats.record("apple", 12)
    stats.record("grape", 84)
    stats.record(("lemon", "apple"), 42, unit="cochren")
    stats.record(("lemon", "grape"), 128, unit="pezeta")
    stats.collect(("lemon", "zest"), 1, unit="pinch")
    stats.collect(("lemon", "zest"), 3)
    stats.collect(("lemon", "zest"), 12)
    stats.collect(("lemon", "zest"), 56)
    stats.collect(("melon", "marry"), 34)
    stats.collect(("melon", "marry"), 34.12)
    stats.collect(("melon", "sweet"), 27)
    stats.collect(("melon", "sweet"), 27.23)
    stats.collect(("melon", "sweet"), 0.27)
    stats.collect(("melon", "sweet"), 2.3)

    with open("demo_ul.html", "w", encoding="utf8") as demo_file:
        ul = stats.as_html_ul()
        demo_file.write(ul)
    assert ul == (
        '<ul class="statistics-list"><li><i class="fas fa-info-circle"></i> '
        '<strong>apple</strong> = 12</li><li><i class="fas fa-info-circle"></i> '
        '<strong>grape</strong> = 84</li><li><i class="fas fa-sitemap"></i> '
        '<strong>lemon</strong> <ul class="statistics-list"><li><i class="fas '
        'fa-info-circle"></i> <strong>apple</strong> = 42 cochren</li><li><i '
        'class="fas fa-info-circle"></i> <strong>grape</strong> = 128 '
        'pezeta</li><li><i class="fas fa-info-circle"></i> <strong>zest</strong> is a '
        'list of numbers<ul class="statistics-list property-list"><li '
        'class="property">average = 18 pinch</li><li class="property">deviation = '
        '25.78113005022601 pinch</li><li class="property">median = 7.5 pinch</li><li '
        'class="property">count = 4</li><li class="property">sum = 72 '
        'pinch</li></ul></li></ul></li><li><i class="fas fa-sitemap"></i> '
        '<strong>melon</strong> <ul class="statistics-list"><li><i class="fas '
        'fa-info-circle"></i> <strong>marry</strong> is a list of numbers<ul '
        'class="statistics-list property-list"><li class="property">average = '
        '34.06</li><li class="property">deviation = 0.08485281374238389</li><li '
        'class="property">median = 34.06</li><li class="property">count = 2</li><li '
        'class="property">sum = 68.12</li></ul></li><li><i class="fas '
        'fa-info-circle"></i> <strong>sweet</strong> is a list of numbers<ul '
        'class="statistics-list property-list"><li class="property">average = '
        '14.2</li><li class="property">deviation = 14.936262361559312</li><li '
        'class="property">median = 14.65</li><li class="property">count = 4</li><li '
        'class="property">sum = 56.800000000000004</li></ul></li></ul></li></ul>'
    )
