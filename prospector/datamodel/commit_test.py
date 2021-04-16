# from dataclasses import asdict
from datamodel.commit import Commit


def test_simple():
    commit = Commit(commit_id="abcd", repository="https://github.com/abc/xyz")

    assert commit.repository == "https://github.com/abc/xyz"

    commit = Commit(commit_id="abcd", repository="https://github.com/abc/xyz")

    assert commit.feature_1 == ""
    # assert commit.as_dict()["repository"] == commit.repository
