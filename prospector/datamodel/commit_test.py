# from dataclasses import asdict
from datamodel.commit import Commit


def test_simple():
    commit = Commit("abcd", "https://github.com/abc/xyz", "X", "Y")

    assert commit.repository == "https://github.com/abc/xyz"

    commit = Commit("abcd", "https://github.com/abc/xyz")

    assert commit.feature_1 == ""
    assert commit.as_dict()["repository"] == commit.repository
