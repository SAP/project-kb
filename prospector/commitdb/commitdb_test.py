from commitdb.postgres import PostgresCommitDB, parse_connect_string
import pytest

import os
db_pass = (os.environ['POSTGRES_PASSWORD'])
connect_string = "HOST=localhost;DB=postgres;UID=postgres;PWD={};PORT=5432;".format(db_pass)

@pytest.fixture
def setupdb():
    db = PostgresCommitDB()
    db.connect(connect_string)
    db.reset()
    return db

def test_simple_write(setupdb):
    db = setupdb
    db.connect(connect_string)
    commit_obj = { 'id': 'abcd1234', 'repository': 'https://github.com/abc/def', 'feat_1': 'A', 'feat_2': 'B'}
    db.save(commit_obj)
    commit_obj = { 'id': 'hijk5678', 'repository': 'https://github.com/opq/str', 'feat_1': 'X', 'feat_2': 'Y'}
    db.save(commit_obj)

def test_simple_read():
    db = PostgresCommitDB()
    db.connect(connect_string)
    commit = { 'hash': 'abcd1234', 'repository': 'https://github.com/abc/def'}
    result = db.lookup( commit )
    print(result)
    assert result is not None

def test_parse_connect_string():
    result = dict()
    parsed_connect_string = parse_connect_string(connect_string)
    assert parsed_connect_string['host'] == 'localhost'
    assert parsed_connect_string['uid'] == 'postgres'
    assert parsed_connect_string['port'] == '5432'
