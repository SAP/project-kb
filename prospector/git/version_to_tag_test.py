import pytest

from .fixtures_test import tags
from .version_to_tag import get_tag_for_version, recursively_split_version_string

# flake8: noqa


@pytest.mark.parametrize(
    "input_version, result",
    [
        ("v2.10.0.Final", ["v", 2, ".", 10, ".", 0, ".Final"]),
        ("4.1.M1", [4, ".", 1, ".M", 1]),
        ("1.1.6", [1, ".", 1, ".", 6]),
        ("1.1.6-RC2", [1, ".", 1, ".", 6, "-RC", 2]),
    ],
)
def test_recursively_split_version_string(input_version, result):
    assert recursively_split_version_string(input_version) == result


@pytest.mark.parametrize("input_version, error", [([1, ".", 1, ".", 6], TypeError)])
def test_recursively_split_version_string_errors(input_version, error):
    with pytest.raises(error):
        recursively_split_version_string(input_version)


@pytest.mark.parametrize(
    "version, tag",
    [
        ("0.1", "docker-plugin-0.1"),
        ("1.2.0", "docker-plugin-1.2.0"),
        ("1.8", "libvirt-slave-1.8"),
    ],
)
def test_get_tag_for_version(version, tag, tags):
    # returns a list of tags that could be corresponding to the version
    assert tag in get_tag_for_version(tags, version)
