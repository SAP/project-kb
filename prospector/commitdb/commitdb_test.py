"""
Unit tests for database-related functionality

"""
from tkinter import E
import pytest

from commitdb.postgres import PostgresCommitDB, parse_connect_string, DB_CONNECT_STRING
from datamodel.commit import Commit, make_from_dict, make_from_raw_commit
from git.git import Git


@pytest.fixture
def setupdb():
    db = PostgresCommitDB()
    db.connect()
    db.reset()
    return db


def test_save_lookup_real(setupdb: PostgresCommitDB):
    repo = Git("https://github.com/slackhq/nebula")
    repo.clone()
    raw_commit = repo.create_commits()
    commit = make_from_raw_commit(list(raw_commit.values())[0])
    commit_2 = make_from_raw_commit(list(raw_commit.values())[1])

    setupdb.save(commit.to_dict())
    setupdb.save(commit_2.to_dict())
    commits = setupdb.lookup(
        "https://github.com/slackhq/nebula",
        "edc283d27a54193d74168a72f054fbf5b5bf21c6,017981a65386d426d8926a5b55d302f3b7c2fb41",
    )

    print(commits)
    raise Exception("test")


def test_lookup(setupdb: PostgresCommitDB):
    commit = setupdb.lookup(
        "https://github.com/slackhq/nebula", "edc283d27a54193d74168a72f054fbf5b5bf21c6"
    )
    print(commit[0])
    raise Exception("test")


def test_save_lookup(setupdb):
    setupdb.connect(DB_CONNECT_STRING)
    commit = Commit(
        commit_id="42423b2423",
        repository="https://fasfasdfasfasd.com/rewrwe/rwer",
        timestamp=121422430,
        hunks=1,
        message="Some random garbage",
        diff=["fasdfasfa", "asf90hfasdfads", "fasd0fasdfas"],
        changed_files=["fadsfasd/fsdafasd/fdsafafdsa.ifd"],
        message_reference_content=[],
        jira_refs={},
        ghissue_refs={"hggdhd": ""},
        cve_refs=["simola3"],
        tags=["tag1"],
    )
    setupdb.save(commit.as_dict())
    result = setupdb.lookup(
        "https://fasfasdfasfasd.com/rewrwe/rwer",
        "42423b2423",
    )

    retrieved_commit = make_from_dict(result[0])
    # setupdb.reset()
    assert commit.commit_id == retrieved_commit.commit_id


def test_lookup_nonexisting(setupdb):
    setupdb.connect(DB_CONNECT_STRING)
    result = setupdb.lookup(
        "https://fasfasdfasfasd.com/rewrwe/rwer",
        "42423b242342423b2423",
    )
    setupdb.reset()
    assert len(result) == 0


def test_parse_connect_string():
    parsed_connect_string = parse_connect_string(DB_CONNECT_STRING)
    assert parsed_connect_string["host"] == "localhost"
    assert parsed_connect_string["user"] == "postgres"
    assert parsed_connect_string["port"] == "5432"
