"""
This module implements an abstraction layer on top of
the underlying database where pre-processed commits are stored
"""
import psycopg2
from psycopg2.extras import NamedTupleCursor

from datamodel.commit import Commit

from . import CommitDB


class PostgresCommitDB(CommitDB):
    """
    This class implements the database abstraction layer
    for PostgreSQL
    """

    def __init__(self):
        self.connect_string = ""
        self.connection_data = dict()
        self.connection = None

    def connect(self, connect_string=None):
        self.connect_string = connect_string.rstrip(";")
        self.connection_data = parse_connect_string(self.connect_string)

        self.connection = psycopg2.connect(
            host=self.connection_data["host"],
            dbname=self.connection_data["db"],
            user=self.connection_data["uid"],
            password=self.connection_data["pwd"],
            cursor_factory=NamedTupleCursor,
        )

    def lookup(self, commit_obj: Commit):
        if not self.connection:
            raise Exception("Invalid connection")

        data = []
        try:
            cur = self.connection.cursor()
            cur.execute(
                "SELECT * FROM commits WHERE repository = %s AND (%s IS NULL OR id = %s)",
                (commit_obj.repository, commit_obj.commit_id, commit_obj.commit_id),
            )
            data = cur.fetchall()
            cur.close()
        except Exception as ex:
            print(ex)
            raise Exception("Could not lookup commit vector in database")

        return data

    def save(self, commit_obj: Commit):
        if not self.connection:
            raise Exception("Invalid connection")

        try:
            cur = self.connection.cursor()
            cur.execute(
                """INSERT INTO commits(
                    id,
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
                    tags)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                        tags) = (
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
                            EXCLUDED.tags)""",
                (
                    commit_obj.commit_id,
                    commit_obj.repository,
                    commit_obj.timestamp,
                    commit_obj.hunks,
                    commit_obj.hunk_count,
                    commit_obj.message,
                    commit_obj.diff,
                    commit_obj.changed_files,
                    commit_obj.message_reference_content,
                    commit_obj.jira_refs,
                    commit_obj.ghissue_refs,
                    commit_obj.cve_refs,
                    commit_obj.tags,
                ),
            )
            self.connection.commit()
        except Exception as exception:
            print(exception)
            # raise Exception("Could not save commit vector to database")

    def reset(self):
        """
        Resets the database by dropping its tables and recreating them afresh.
        If the database does not exist, or any tables are missing, they
        are created.
        """

        if not self.connection:
            raise Exception("Invalid connection")

        self._run_sql_script("ddl/commit.sql")
        self._run_sql_script("ddl/users.sql")

    def _run_sql_script(self, script_file):
        if not self.connection:
            raise Exception("Invalid connection")

        with open(script_file, "r") as file:
            ddl = file.read()

        cursor = self.connection.cursor()
        cursor.execute(ddl)
        self.connection.commit()

        cursor.close()


def parse_connect_string(connect_string):
    # TODO convert to better connection string format
    # https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
    result = dict()
    connect_string = connect_string.rstrip(";")
    try:
        parsed_string = [e.split("=") for e in connect_string.split(";")]
        for key, value in parsed_string:
            result[key.lower()] = value
    except Exception:
        raise Exception("Invalid connect string: " + connect_string)

    return dict(result)
