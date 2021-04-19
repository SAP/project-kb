from datamodel.commit import Commit
from datamodel.commit_features import CommitFeatures


def test_simple():
    commit = Commit(
        commit_id="abcd",
        repository="https://github.com/abc/xyz",
        timestamp="124234125",
    )
    commit_features = CommitFeatures(commit=commit, references_vuln_id=True)

    assert commit_features.commit.repository == "https://github.com/abc/xyz"
    assert commit_features.references_vuln_id
