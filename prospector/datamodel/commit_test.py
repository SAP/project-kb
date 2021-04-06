from dataclasses import asdict
from datamodel.commit import Commit
import pytest


def test_simple():
    c = Commit("abcd", "https://github.com/abc/xyz", "X", "Y")

    assert c.repository == "https://github.com/abc/xyz"

    c = Commit("abcd", "https://github.com/abc/xyz")

    assert c.feature_1 == ""
    assert c.asDict()["repository"] == c.repository
