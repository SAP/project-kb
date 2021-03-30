from commitdb.postgres import PostgresCommitDB, parse_connect_string

import os
db_pass = (os.environ['POSTGRES_PASSWORD'])
connect_string = "HOST=localhost;DB=postgres;UID=postgres;PWD={};PORT=5432;".format(db_pass)

def test_simple_read():
    db = PostgresCommitDB()
    db.connect(connect_string)
    commit = ('abcd', 'https://github.com/abc/def')
    result = db.lookup( commit )
    assert len(result) > 0

def test_simple_write():
    db = PostgresCommitDB()
    db.connect(connect_string)
    commit = ('abcd', 'https://github.com/abc/def')
    db.save(commit)

def test_parse_connect_string():
    result = dict()
    parsed_connect_string = parse_connect_string(connect_string)
    assert parsed_connect_string['host'] == 'localhost'
    assert parsed_connect_string['uid'] == 'postgres'
    assert parsed_connect_string['port'] == '5432'
