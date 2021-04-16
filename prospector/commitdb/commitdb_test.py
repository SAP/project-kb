"""
Unit tests for database-related functionality

"""
import os

import pytest

from commitdb.postgres import PostgresCommitDB, parse_connect_string
from datamodel.commit import Commit

CONNECT_STRING = "HOST=127.0.0.1;DB=postgres;UID=postgres;PWD={};PORT=5432;".format(
    os.environ["POSTGRES_PASSWORD"]
)


@pytest.fixture
def setupdb():
    db = PostgresCommitDB()
    db.connect(CONNECT_STRING)
    db.reset()
    return db


def test_simple_write(setupdb):
    db = setupdb
    db.connect(CONNECT_STRING)
    commit_obj = Commit(
        commit_id="1234",
        repository="https://blabla.com/zxyufd/fdafa",
        feature_1="",
        timestamp=123456789,
        hunks=[(3, 5)],
        hunk_count=1,
        message="Some random garbage",
        diff=["fasdfasfa", "asf90hfasdfads", "fasd0fasdfas"],
        changed_files=["fadsfasd/fsdafasd/fdsafafdsa.ifd"],
        message_reference_content=[],
        jira_refs=[],
        ghissue_refs=[],
        cve_refs=["fasdfads", "fsfasf"],
    )
    # commit_obj = Commit(
    #     commit_id="abcd1234",
    #     repository="https://github.com/abc/def",
    #     "A",
    #     1212444,
    #     "hunk1",
    #     1,
    #     "Test commit",
    #     "-",
    #     "test.py",
    #     "none",
    #     "https://jira...com",
    #     "https://ghissue...com",
    #     "https://cve...com",
    # )
    db.save(commit_obj)
    commit_obj = Commit(
        commit_id="42423b2423",
        repository="https://fasfasdfasfasd.com/rewrwe/rwer",
        feature_1="xxxxxxxxx",
        timestamp=121422430,
        hunks=[(3, 5)],
        hunk_count=1,
        message="Some random garbage",
        diff=["fasdfasfa", "asf90hfasdfads", "fasd0fasdfas"],
        changed_files=["fadsfasd/fsdafasd/fdsafafdsa.ifd"],
        message_reference_content=[],
        jira_refs=[],
        ghissue_refs=["hggdhd"],
        cve_refs=["fasdfads", "fsfasf"],
    )
    db.save(commit_obj)


def test_simple_read():
    db = PostgresCommitDB()
    db.connect(CONNECT_STRING)
    commit_obj = Commit(
        commit_id="1234",
        repository="https://blabla.com/zxyufd/fdafa",
        feature_1="",
        timestamp=0,
        hunks=[(3, 5)],
        hunk_count=1,
        message="Some random garbage",
        diff=["fasdfasfa", "asf90hfasdfads", "fasd0fasdfas"],
        changed_files=["fadsfasd/fsdafasd/fdsafafdsa.ifd"],
        message_reference_content=[],
        jira_refs=[],
        ghissue_refs=[],
        cve_refs=["fasdfads", "fsfasf"],
    )
    result = db.lookup(commit_obj)
    print(result)
    db.reset()  # remove garbage added by tests from DB
    assert result is not None


def test_parse_connect_string():
    # result = dict()
    parsed_connect_string = parse_connect_string(CONNECT_STRING)
    assert parsed_connect_string["host"] == "127.0.0.1"
    assert parsed_connect_string["uid"] == "postgres"
    assert parsed_connect_string["port"] == "5432"
