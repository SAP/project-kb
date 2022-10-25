"""
This module implements an abstraction layer on top of
the underlying database where pre-processed commits are stored
"""
import os

from typing import Dict, List, Any
import psycopg2

from psycopg2.extensions import parse_dsn
from psycopg2.extras import DictCursor, DictRow, Json
from commitdb import CommitDB

from log.logger import logger

DB_CONNECT_STRING = "postgresql://{}:{}@{}:{}/{}".format(
    os.getenv("POSTGRES_USER", "postgres"),
    os.getenv("POSTGRES_PASSWORD", "example"),
    os.getenv("POSTGRES_HOST", "localhost"),
    os.getenv("POSTGRES_PORT", "5432"),
    os.getenv("POSTGRES_DBNAME", "postgres"),
).lower()


class PostgresCommitDB(CommitDB):
    """
    This class implements the database abstraction layer
    for PostgreSQL
    """

    def __init__(self):
        self.connect_string = ""
        self.connection = None

    def connect(self, connect_string=DB_CONNECT_STRING):
        self.connection = psycopg2.connect(connect_string)

    def query(self, query: str):
        if not self.connection:
            raise Exception("Invalid connection")
        self.connection.cursor().execute(query)

    def lookup(self, repository: str, commit_id: str = None) -> List[Dict[str, Any]]:
        if not self.connection:
            raise Exception("Invalid connection")

        try:
            cur = self.connection.cursor(cursor_factory=DictCursor)

            if commit_id is None:
                cur.execute(
                    "SELECT * FROM commits WHERE repository = %s", (repository,)
                )
            else:
                for id in commit_id.split(","):
                    cur.execute(
                        "SELECT * FROM commits WHERE repository = %s AND commit_id = %s",
                        (repository, id),
                    )
                    results.append(cur.fetchone())

            result = cur.fetchall()
            cur.close()
            return [dict(row) for row in result]  # parse_commit_from_db
        except Exception:
            logger.error("Could not lookup commit vector in database", exc_info=True)
            cur.close()
            return None
            raise Exception("Could not lookup commit vector in database")

    def save(self, commit: Dict[str, Any]):
        if not self.connection:
            raise Exception("Invalid connection")

        try:
            cur = self.connection.cursor()
            statement = build_statement(commit)
            args = get_args(commit)
            cur.execute(statement, args)
            self.connection.commit()
            cur.close()
        except Exception:
            logger.error("Could not save commit vector to database", exc_info=True)
            cur.close()
            # raise Exception("Could not save commit vector to database")

    def reset(self):
        self.run_sql_script("ddl/10_commit.sql")
        self.run_sql_script("ddl/20_users.sql")

    def run_sql_script(self, script_file):
        if not self.connection:
            raise Exception("Invalid connection")

        with open(script_file, "r") as file:
            ddl = file.read()

        cursor = self.connection.cursor()
        cursor.execute(ddl)
        self.connection.commit()

        cursor.close()


def parse_connect_string(connect_string):
    try:
        return parse_dsn(connect_string)
    except Exception:
        raise Exception(f"Invalid connect string: {connect_string}")


def build_statement(data: Dict[str, Any]):
    columns = ",".join(data.keys())
    on_conflict = ",".join([f"EXCLUDED.{key}" for key in data.keys()])
    return f"INSERT INTO commits ({columns}) VALUES ({','.join(['%s'] * len(data))}) ON CONFLICT ON CONSTRAINT commits_pkey DO UPDATE SET ({columns}) = ({on_conflict})"


def get_args(data: Dict[str, Any]):
    return tuple([Json(val) if isinstance(val, dict) else val for val in data.values()])


def parse_commit_from_db(raw_data: DictRow) -> Dict[str, Any]:
    out = dict(raw_data)
    out["hunks"] = [(int(x[1]), int(x[3])) for x in raw_data["hunks"]]
    return out
