from commitdb.postgres import PostgresCommitDB, parse_connect_string
from datamodel.commit import Commit

import pytest

import os

db_pass = os.environ["POSTGRES_PASSWORD"]
connect_string = "HOST=localhost;DB=postgres;UID=postgres;PWD={};PORT=5432;".format(
    db_pass
)


@pytest.fixture
def setupdb():
    db = PostgresCommitDB()
    db.connect(connect_string)
    db.reset()
    return db


def test_simple_write(setupdb):
    db = setupdb
    db.connect(connect_string)
    commit_obj = Commit("abcd1234", "https://github.com/abc/def", "A", "B")
    db.save(commit_obj)
    commit_obj = Commit("hijk5678", "https://github.com/opq/str", "X", "Y")
    db.save(commit_obj)


def test_simple_read():
    db = PostgresCommitDB()
    db.connect(connect_string)
    commit_obj = Commit("abcd1234", "https://github.com/abc/def", "A", "B")
    result = db.lookup(commit_obj)
    print(result)
    assert result is not None


def test_parse_connect_string():
    result = dict()
    parsed_connect_string = parse_connect_string(connect_string)
    assert parsed_connect_string["host"] == "localhost"
    assert parsed_connect_string["uid"] == "postgres"
    assert parsed_connect_string["port"] == "5432"
