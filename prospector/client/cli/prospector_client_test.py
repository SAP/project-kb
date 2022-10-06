import pytest

from api import DB_CONNECT_STRING
from client.cli.prospector_client import build_advisory_record
from commitdb.postgres import PostgresCommitDB
from stats.execution import execution_statistics

from .main import main

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
    db.connect(DB_CONNECT_STRING)
    db.reset()
    return db


def test_main_runonce(setupdb):
    db = setupdb
    db.connect(DB_CONNECT_STRING)
    args = [
        "PROGRAM_NAME",
        "CVE-2019-11278",
        "--repository",
        "https://github.com/cloudfoundry/uaa",
        "--tag-interval=v74.0.0:v74.1.0",
        "--use-backend=optional",
    ]
    execution_statistics.drop_all()
    main(args)
    db.reset()


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
