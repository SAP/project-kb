import subprocess

import pytest

from commitdb.postgres import PostgresCommitDB

# from .prospector_client import prospector

# def test_prospector_client():
#     results = prospector(
#         "CVE-2014-0050",
#         "https://github.com/apache/struts",
#         publication_date="2016-12-12T12:18Z",
#         debug=True,
#     )
#     pprint(results)


@pytest.fixture
def setupdb():
    db = PostgresCommitDB()
    db.connect()
    db.reset()
    return db


@pytest.mark.skip(reason="not implemented yet")
def test_main_runonce(setupdb: PostgresCommitDB):
    args = [
        "python",
        "main.py",
        "CVE-2019-11278",
        "--repository",
        "https://github.com/cloudfoundry/uaa",
        "--tag-interval=v74.0.0:v74.1.0",
        "--use-backend=optional",
    ]
    subprocess.run(args)

    setupdb.reset()


# def test_main_runtwice(setupdb):
#     db = setupdb
#     db.connect(DB_CONNECT_STRING)
#     args = [
#         "PROGRAM_NAME",
#         "CVE-2019-11278",
#         "--repository",
#         "https://github.com/cloudfoundry/uaa",
#         "--tag-interval=v74.0.0:v74.1.0",
#     ]
#     main(args)
#     main(args)
#     db.reset()


# def test_main_ping_server():
#     args = ["PROGRAM_NAME", "--verbose", "--ping"]
#     assert main(args)
