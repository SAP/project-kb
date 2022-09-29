"""
Unit tests for database-related functionality

"""
import pytest

from api import DB_CONNECT_STRING
from commitdb.postgres import PostgresCommitDB, parse_connect_string
from datamodel.commit import Commit


# @pytest.fixture
def setupdb():
    db = PostgresCommitDB()
    db.connect(DB_CONNECT_STRING)
    db.reset()
    return db


def test_simple_write(setupdb):
    db = setupdb
    db.connect(DB_CONNECT_STRING)
    commit_obj = Commit(
        commit_id="1234",
        repository="https://blabla.com/zxyufd/fdafa",
        timestamp=123456789,
        hunks=[(3, 5)],
        hunk_count=1,
        message="Some random garbage",
        diff=["fasdfasfa", "asf90hfasdfads", "fasd0fasdfas"],
        changed_files=["fadsfasd/fsdafasd/fdsafafdsa.ifd"],
        message_reference_content=[],
        jira_refs={},
        ghissue_refs={},
        cve_refs={"fasdfads": "", "fsfasf": ""},
        tags=["tag1"],
    )
    db.save(commit_obj)
    commit_obj = Commit(
        commit_id="42423b2423",
        repository="https://fasfasdfasfasd.com/rewrwe/rwer",
        timestamp=121422430,
        hunks=[(3, 5)],
        hunk_count=1,
        message="Some random garbage",
        diff=["fasdfasfa", "asf90hfasdfads", "fasd0fasdfas"],
        changed_files=["fadsfasd/fsdafasd/fdsafafdsa.ifd"],
        message_reference_content=[],
        jira_refs={},
        ghissue_refs={"hggdhd": ""},
        cve_refs={"fasdfads": "", "fsfasf": ""},
        tags=["tag1"],
    )
    db.save(commit_obj)


def test_lookup():
    db = PostgresCommitDB()
    db.connect(DB_CONNECT_STRING)
    result = db.lookup(
        "https://github.com/apache/maven-shared-utils",
        "f751e614c09df8de1a080dc1153931f3f68991c9",
    )
    print([d.dict() for d in result])
    assert result is not None


def test_upsert(setupdb):
    db = PostgresCommitDB()
    db.connect(DB_CONNECT_STRING)
    commit_obj = Commit(
        commit_id="42423b2423",
        repository="https://fasfasdfasfasd.com/rewrwe/rwer",
        timestamp=1214212430,
        hunks=[(3, 3)],
        hunk_count=3,
        message="Some random garbage upserted",
        diff=["fasdfasfa", "asf90hfasdfads", "fasd0fasdfas"],
        changed_files=["fadsfasd/fsdafasd/fdsafafdsa.ifd"],
        message_reference_content=[],
        jira_refs={},
        ghissue_refs={"hggdhd": ""},
        cve_refs={"fasdfads": "", "314202": ""},
        tags=["tag1"],
    )
    db.save(commit_obj)
    result = db.lookup(commit_obj.repository, commit_obj.commit_id)
    assert result is not None
    db.reset()  # remove garbage added by tests from DB


def test_parse_connect_string():
    parsed_connect_string = parse_connect_string(DB_CONNECT_STRING)
    assert parsed_connect_string["host"] == "localhost"
    assert parsed_connect_string["user"] == "postgres"
    assert parsed_connect_string["port"] == "5432"


if __name__ == "__main__":
    test_lookup()
