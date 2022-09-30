"""
This module implements an abstraction layer on top of
the underlying database where pre-processed commits are stored
"""
import re
from typing import List, Tuple
import psycopg2
import psycopg2.sql
from psycopg2.extensions import parse_dsn
from psycopg2.extras import DictCursor, DictRow

import log.util
from datamodel.commit import Commit

from . import CommitDB

_logger = log.util.init_local_logger()


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
                        data.append(parse_commit_from_database(result[0]))
                    # if not len(result):
                    #     # Workaround for unmarshaling hunks, dict type refs
                    #     hunks = [
                    #         int(x)
                    #         for x in re.findall("[0-9]+", "".join(result[0]["hunks"]))
                    #     ]
                    #     # They are always pairs so no problem
                    #     result[0]["hunks"] = list(zip(hunks, hunks[2:]))

                    #     result[0]["jira_refs_id"] = dict(
                    #         zip(
                    #             result[0]["jira_refs_id"],
                    #             result[0]["jira_refs_content"],
                    #         )
                    #     )
                    #     result[0]["ghissue_refs_id"] = dict(
                    #         zip(
                    #             result[0]["ghissue_refs_id"],
                    #             result[0]["ghissue_refs_content"],
                    #         )
                    #     )
                    #     result[0]["cve_refs"] = list(result[0]["cve_refs"])
                    #     # result[0]["cve_refs"] = dict.fromkeys(result[0]["cve_refs"], "")
                    #     parsed_commit = Commit.parse_obj(result[0])

                    #     data.append(parsed_commit)
                    # else:
                    #     data.append(parse_commit(result[0]))
                    #    data.append(None)
            else:
                raise Exception(
                    "ABORT: Why are you getting every commit of a repository? "
                )
                cur.execute(
                    "SELECT * FROM commits WHERE repository = %s",
                    (repository,),
                )
                result = cur.fetchall()
                if len(result):
                    for res in result:
                        # Workaround for unmarshaling hunks, dict type refs
                        lis = []
                        for r in res[3]:
                            a, b = r.strip("()").split(",")
                            lis.append((int(a), int(b)))
                        res[3] = lis
                        res[9] = dict.fromkeys(res[8], "")
                        res[10] = dict.fromkeys(res[9], "")
                        res[11] = dict.fromkeys(res[10], "")
                        parsed_commit = Commit.parse_obj(res)
                        data.append(parsed_commit)
            cur.close()
        except Exception:
            _logger.error("Could not lookup commit vector in database", exc_info=True)
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
                    jira_refs_id,
                    jira_refs_content,
                    ghissue_refs_id,
                    ghissue_refs_content,
                    cve_refs,
                    tags)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT ON CONSTRAINT commits_pkey DO UPDATE SET (
                        timestamp,
                        hunks,
                        hunk_count,
                        message,
                        diff,
                        changed_files,
                        message_reference_content,
                        jira_refs_id,
                        jira_refs_content,
                        ghissue_refs_id,
                        ghissue_refs_content,
                        cve_refs,
                        tags) = (
                            EXCLUDED.timestamp,
                            EXCLUDED.hunks,
                            EXCLUDED.hunk_count,
                            EXCLUDED.message,
                            EXCLUDED.diff,
                            EXCLUDED.changed_files,
                            EXCLUDED.message_reference_content,
                            EXCLUDED.jira_refs_id,
                            EXCLUDED.jira_refs_content,
                            EXCLUDED.ghissue_refs_id,
                            EXCLUDED.ghissue_refs_content,
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
                    list(commit_obj.jira_refs.keys()),
                    list(commit_obj.jira_refs.values()),
                    list(commit_obj.ghissue_refs.keys()),
                    list(commit_obj.ghissue_refs.values()),
                    commit_obj.cve_refs,
                    commit_obj.tags,
                ),
            )
            self.connection.commit()
        except Exception:
            _logger.error("Could not save commit vector to database", exc_info=True)
            # raise Exception("Could not save commit vector to database")

    def reset(self):
        """
        Resets the database by dropping its tables and recreating them afresh.
        If the database does not exist, or any tables are missing, they
        are created.
        """

        if not self.connection:
            raise Exception("Invalid connection")

        self._run_sql_script("ddl/10_commit.sql")
        self._run_sql_script("ddl/20_users.sql")

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


def parse_commit_from_database(raw_commit_data: DictRow) -> Commit:
    """
    This function is responsible of parsing a preprocessed commit from the database
    """
    commit = Commit(
        commit_id=raw_commit_data["commit_id"],
        repository=raw_commit_data["repository"],
        timestamp=int(raw_commit_data["timestamp"]),
        hunks=parse_hunks(raw_commit_data["hunks"]),
        message=raw_commit_data["message"],
        diff=raw_commit_data["diff"],
        changed_files=raw_commit_data["changed_files"],
        message_reference_content=raw_commit_data["message_reference_content"],
        jira_refs=dict(
            zip(raw_commit_data["jira_refs_id"], raw_commit_data["jira_refs_content"])
        ),
        ghissue_refs=dict(
            zip(
                raw_commit_data["ghissue_refs_id"],
                raw_commit_data["ghissue_refs_content"],
            )
        ),
        cve_refs=raw_commit_data["cve_refs"],
        tags=raw_commit_data["tags"],
    )
    return commit


def parse_hunks(raw_hunks: List[str]) -> List[Tuple[int, int]]:
    """
    This function is responsible of extracting the hunks from a commit
    """
    hunks = []
    for hunk in raw_hunks:
        a, b = hunk.strip("()").split(",")
        hunks.append((int(a), int(b)))
    return hunks
