from datamodel.commit import Commit
from datamodel.commit_features import CommitFeatures


def test_simple():
    commit = Commit("abcd", "https://github.com/abc/xyz", "X", "Y")
    commit_features = CommitFeatures(commit, True)

    assert commit_features.commit.repository == "https://github.com/abc/xyz"
    assert commit_features.reference_to_vuln_id
