# from dataclasses import asdict
import pytest

from git.git import Git

from .commit import make_from_raw_commit


@pytest.fixture
def repository():
    repo = Git("https://github.com/apache/struts")
    repo.clone()
    return repo


def test_proprocess_commit(repository):

    repo = repository
    raw_commit = repo.get_commit("93f378809cc73c65c1d689a0e32ec440c52e7ce2")

    commit = make_from_raw_commit(raw_commit)

    assert commit.message.startswith(
        "Merge pull request #480 from apache/WW-5117-reorders-stack [WW-5117]"
    )

    assert commit.jira_refs == {"WW-5117": ""}
    assert commit.ghissue_refs == {"#480": ""}
    assert commit.cve_refs == {}


def test_proprocess_commit_set(repository):

    repo = repository
    commit_set = repo.get_commits(
        since="1615441712", until="1617441712", filter_files="*.java"
    )
    preprocessed_commits = []

    for commit_id in commit_set:
        raw_commit = repo.get_commit(commit_id)
        preprocessed_commits.append(make_from_raw_commit(raw_commit))

    assert len(preprocessed_commits) == len(commit_set)
