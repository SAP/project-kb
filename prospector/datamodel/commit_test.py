from datamodel.commit import Commit
import pytest


def test_simple():
    c = Commit("abcd", "https://github.com/abc/xyz", "X", "Y")

    assert c.repository == "https://github.com/abc/xyz"
