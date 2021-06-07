"""
This module implements an abstraction layer on top of
the underlying database where pre-processed commits are stored
"""
import psycopg2
import psycopg2.sql
from psycopg2.extensions import parse_dsn
from psycopg2.extras import DictCursor

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
        parse_connect_string(connect_string)
        self.connection = psycopg2.connect(connect_string)

    def lookup(self, repository: str, commit_id: str = None):
        # Returns the results of the query as list of Commit objects
        if not self.connection:
            raise Exception("Invalid connection")

        data = []
        try:
            cur = self.connection.cursor(cursor_factory=DictCursor)
            if commit_id:
                for cid in commit_id.split(","):
                    cur.execute(
                        "SELECT * FROM commits WHERE repository = %s AND commit_id =%s",
                        (
                            repository,
                            cid,
                        ),
                    )

                    result = cur.fetchall()
                    if len(result):
                        # TODO do better than eval
                        lis = []
                        for r in result[0]["hunks"]:
                            lis.append(eval(r))
                        result[0]["hunks"] = lis
                        parsed_commit = Commit.parse_obj(result[0])
                        data.append(parsed_commit)
                    else:
                        data.append(None)
            else:
                cur.execute(
                    "SELECT * FROM commits WHERE repository = %s",
                    (repository,),
                )
                result = cur.fetchall()
                if len(result):
                    for res in result:
                        lis = []
                        for r in res[3]:
                            # TODO do better than eval
                            lis.append(eval(r))
                        res[3] = lis
                        parsed_commit = Commit.parse_obj(res)
                        data.append(parsed_commit)
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
    # According to:
    # https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING

    try:
        parsed_string = parse_dsn(connect_string)
    except Exception:
        raise Exception("Invalid connect string: " + connect_string)

    return parsed_string
