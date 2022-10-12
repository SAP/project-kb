"""
This module implements an abstraction layer on top of
the underlying database where pre-processed commits are stored
"""
from typing import Dict, List, Any
import psycopg2

# import psycopg2.sql
from psycopg2.extensions import parse_dsn
from psycopg2.extras import DictCursor, DictRow, Json

import log.util

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

    def lookup(self, repository: str, commit_id: str = None) -> List[Dict[str, Any]]:
        # Returns the results of the query as list of dicts
        if not self.connection:
            raise Exception("Invalid connection")

        results = list()
        try:
            cur = self.connection.cursor(cursor_factory=DictCursor)
            if commit_id:
                for id in commit_id.split(","):
                    cur.execute(
                        "SELECT * FROM commits WHERE repository = %s AND commit_id = %s",
                        (
                            repository,
                            id,
                        ),
                    )

                    result = cur.fetchall()
                    if len(result):
                        data.append(parse_commit_from_database(result[0]))
            else:
                cur.execute("SELECT * FROM commits WHERE repository = %s", repository)
                result = cur.fetchall()
                for row in result:
                    data.append(parse_commit_from_database(row))
            cur.close()
        except Exception:
            logger.error("Could not lookup commit vector in database", exc_info=True)
            return []
        finally:
            cur.close()

    # TODO: use dict to eliminate dependencies from commit and avoid loading spacy in the backend
    def save(self, commit: Dict[str, Any]):
        if not self.connection:
            raise Exception("Invalid connection")

        try:
            cur = self.connection.cursor()
            cur.execute(
                """INSERT INTO commits(
                    commit_id,
                    repository,
                    timestamp,
                    hunks,
                    hunk_count,
                    message,
                    diff,
                    changed_files,
                    message_reference_content,
                    jira_refs,
                    ghissue_refs,
                    cve_refs,
                    tags,
                    minhash)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT ON CONSTRAINT commits_pkey DO UPDATE SET (
                        timestamp,
                        hunks,
                        hunk_count,
                        message,
                        diff,
                        changed_files,
                        message_reference_content,
                        jira_refs,
                        ghissue_refs,
                        cve_refs,
                        tags,
                        minhash) = (
                            EXCLUDED.timestamp,
                            EXCLUDED.hunks,
                            EXCLUDED.hunk_count,
                            EXCLUDED.message,
                            EXCLUDED.diff,
                            EXCLUDED.changed_files,
                            EXCLUDED.message_reference_content,
                            EXCLUDED.jira_refs,
                            EXCLUDED.ghissue_refs,
                            EXCLUDED.cve_refs,
                            EXCLUDED.tags,
                            EXCLUDED.minhash)""",
                (
                    commit.get("commit_id"),
                    commit.get("repository"),
                    commit.get("timestamp"),
                    commit.get("hunks"),
                    commit.get("hunk_count"),
                    commit.get("message"),
                    commit.get("diff"),
                    commit.get("changed_files"),
                    commit.get("message_reference_content"),
                    Json(commit.get("jira_refs")),
                    Json(commit.get("ghissue_refs")),
                    commit.get("cve_refs"),
                    commit.get("tags"),
                    commit.get("minhash"),
                ),
            )
            self.connection.commit()
            cur.close()
        except Exception:
            logger.error("Could not save commit vector to database", exc_info=True)
            cur.close()

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

def parse_commit_from_database(raw_data: DictRow) -> Dict[str, Any]:
    """
    This function is responsible of parsing a preprocessed commit from the database
    """
    return {
        "commit_id": raw_data["commit_id"],
        "repository": raw_data["repository"],
        "timestamp": raw_data["timestamp"],
        "hunks": [
            (int(x[0]), int(x[1])) for x in raw_data["hunks"]
        ],  # Converts to tuples of ints
        "hunk_count": raw_data["hunk_count"],
        "message": raw_data["message"],
        "diff": raw_data["diff"],
        "changed_files": raw_data["changed_files"],
        "message_reference_content": raw_data["message_reference_content"],
        "jira_refs": raw_data["jira_refs"],
        "ghissue_refs": raw_data["ghissue_refs"],
        "cve_refs": raw_data["cve_refs"],
        "tags": raw_data["tags"],
        "minhash": raw_data["minhash"],
    }
