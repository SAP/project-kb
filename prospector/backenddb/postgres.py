"""
This module implements an abstraction layer on top of
the underlying database where pre-processed commits are stored
"""
import os
from typing import Any, Dict, List

import psycopg2
from psycopg2.extensions import parse_dsn
from psycopg2.extras import DictCursor, DictRow, Json, RealDictCursor

from backenddb import BackendDB
from log.logger import logger

# DB_CONNECT_STRING = "postgresql://{}:{}@{}:{}/{}".format(
#     os.getenv("POSTGRES_USER", "postgres"),
#     os.getenv("POSTGRES_PASSWORD", "example"),
#     os.getenv("POSTGRES_HOST", "localhost"),
#     os.getenv("POSTGRES_PORT", "5432"),
#     os.getenv("POSTGRES_DBNAME", "postgres"),
# ).lower()


class PostgresBackendDB(BackendDB):
    """
    This class implements the database abstraction layer
    for PostgreSQL
    """

    def __init__(self, user, password, host, port, dbname):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.dbname = dbname
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                database=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
            print("Connected to the database")
        except Exception:
            self.host = "localhost"
            self.connection = psycopg2.connect(
                database=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Disconnected from the database")
            self.connection = None
        else:
            print("No active database connection")

    def lookup(self, repository: str, commit_id: str = None) -> List[Dict[str, Any]]:
        if not self.connection:
            raise Exception("Invalid connection")

        results = list()
        try:
            cur = self.connection.cursor(cursor_factory=DictCursor)

            if commit_id is None:
                cur.execute(
                    "SELECT * FROM commits WHERE repository = %s", (repository,)
                )
                if cur.rowcount > 0:
                    results = cur.fetchall()
            else:
                for id in commit_id.split(","):
                    cur.execute(
                        "SELECT * FROM commits WHERE repository = %s AND commit_id = %s",
                        (repository, id),
                    )
                    if cur.rowcount > 0:
                        results.append(cur.fetchone())
            return [dict(row) for row in results]  # parse_commit_from_db
        except Exception:
            logger.error("Could not lookup commit vector in database", exc_info=True)
            return []
        finally:
            cur.close()

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

    def lookup_vuln_id(self, vuln_id: str, last_modified_date):
        if not self.connection:
            raise Exception("Invalid connection")
        results = None
        try:
            cur = self.connection.cursor(cursor_factory=DictCursor)
            cur.execute(
                "SELECT COUNT(*) FROM vulnerability WHERE vuln_id = %s AND last_modified_date = %s",
                (vuln_id, last_modified_date),
            )
            # cur = self.connection.cursor()
            # cur.execute("SELECT * FROM vulnerability WHERE vuln_id = %s", (vuln_id,))
            results = cur.fetchone()
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            logger.error("Could not lookup vulnerability in database", exc_info=True)
        finally:
            cur.close()
        return results

    def lookup_vuln(self, vuln_id: str):
        if not self.connection:
            raise Exception("Invalid connection")
        results = None
        try:
            cur = self.connection.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT * FROM vulnerability WHERE vuln_id = %s", (vuln_id,))
            results = cur.fetchone()
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            logger.error("Could not lookup vulnerability in database", exc_info=True)
        finally:
            cur.close()
        return results

    def lookup_vulnList(self):
        if not self.connection:
            raise Exception("Invalid connection")
        results = []
        try:
            cur = self.connection.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT * FROM vulnerability")
            results = cur.fetchall()
        except Exception:
            logger.error(
                "Could not retrieve vulns from database",
                exc_info=True,
            )
        finally:
            cur.close()
        return results

    def save_vuln(
        self,
        vuln_id: str,
        published_date: str,
        last_modified_date: str,
        raw_record: Json,
        source: str,
        url: str,
    ):
        if not self.connection:
            raise Exception("Invalid connection")

        try:
            cur = self.connection.cursor()
            cur.execute(
                "INSERT INTO vulnerability (vuln_id, published_date, last_modified_date, raw_record, source, url) VALUES (%s,%s,%s,%s,%s,%s)",
                (vuln_id, published_date, last_modified_date, raw_record, source, url),
            )
            self.connection.commit()
            cur.close()
        except Exception:
            logger.error("Could not save vulnerability to database", exc_info=True)
            cur.close()

    def save_job(
        self,
        _id: str,
        pv_id: int,
        params: str,
        enqueued_at: str,
        started_at: str,
        finished_at: str,
        results: str,
        created_by: str,
        status: str,
    ):
        if not self.connection:
            raise Exception("Invalid connection")
        try:
            cur = self.connection.cursor()
            cur.execute(
                "INSERT INTO job (_id, pv_id, params, enqueued_at, started_at, finished_at, results, created_by, status)"
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    _id,
                    pv_id,
                    params,
                    enqueued_at,
                    started_at,
                    finished_at,
                    results,
                    created_by,
                    status,
                ),
            )
            self.connection.commit()
            cur.close()
        except Exception:
            logger.error("Could not save job entry to database", exc_info=True)
            cur.close()

    def save_manual_job(
        self,
        _id: str,
        params: str,
        enqueued_at: str,
        started_at: str,
        finished_at: str,
        results: str,
        created_by: str,
        status: str,
    ):
        if not self.connection:
            raise Exception("Invalid connection")
        params
        try:
            cur = self.connection.cursor()

            # Divide job.args into separate elements
            vuln_id, repo, versions = params

            # Insert into vulnerability table
            cur.execute(
                "INSERT INTO vulnerability (vuln_id, last_modified_date, source) "
                "VALUES (%s, %s, %s)",
                (vuln_id, enqueued_at, created_by),
            )

            # Retrieve the newly inserted vulnerability ID
            cur.execute("SELECT _id FROM vulnerability WHERE vuln_id = %s", (vuln_id,))
            vulnerability_id = cur.fetchone()[0]

            # Insert into processed_vuln table
            cur.execute(
                "INSERT INTO processed_vuln (fk_vulnerability, repository, versions) "
                "VALUES (%s, %s, %s)",
                (vulnerability_id, repo, versions),
            )

            # Retrieve the newly inserted processed_vuln ID
            cur.execute(
                "SELECT _id FROM processed_vuln WHERE fk_vulnerability = %s",
                (vulnerability_id,),
            )
            processed_vuln_id = cur.fetchone()[0]

            # Insert into job table
            cur.execute(
                "INSERT INTO job (_id, pv_id, params, enqueued_at, started_at, finished_at, results, created_by, status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    _id,
                    processed_vuln_id,
                    params,
                    enqueued_at,
                    started_at,
                    finished_at,
                    results,
                    created_by,
                    status,
                ),
            )

            self.connection.commit()
            cur.close()
        except Exception:
            logger.error("Could not save job entry to database", exc_info=True)
            cur.close()

    def save_dependent_job(
        self,
        parent_id: str,
        _id: str,
        params: str,
        enqueued_at: str,
        started_at: str,
        finished_at: str,
        results: str,
        created_by: str,
        status: str,
    ):
        if not self.connection:
            raise Exception("Invalid connection")
        params
        try:
            cur = self.connection.cursor()

            # retrieve parent job
            parent_job = self.lookup_job_id(parent_id)
            created_from = parent_job["_id"]
            parent_job_pv_id = parent_job["pv_id"]

            # Insert child job into job table
            cur.execute(
                "INSERT INTO job (_id, pv_id, params, enqueued_at, started_at, finished_at, results, created_by, created_from, status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    _id,
                    parent_job_pv_id,
                    params,
                    enqueued_at,
                    started_at,
                    finished_at,
                    results,
                    created_by,
                    created_from,
                    status,
                ),
            )

            self.connection.commit()
            cur.close()
        except Exception:
            logger.error("Could not save job entry to database", exc_info=True)
            cur.close()

    def lookup_job(self):
        if not self.connection:
            raise Exception("Invalid connection")
        results = []
        try:
            cur = self.connection.cursor(cursor_factory=DictCursor)
            cur.execute("SELECT * FROM job")
            results = cur.fetchall()
        except Exception:
            logger.error("Could not retrieve jobs from database", exc_info=True)
        finally:
            cur.close()
        return results

    def lookup_processed_no_job(self):
        if not self.connection:
            raise Exception("Invalid connection")
        results = []
        try:
            cur = self.connection.cursor(cursor_factory=DictCursor)
            cur.execute(
                "SELECT _id FROM processed_vuln WHERE _id NOT IN ( SELECT pv_id FROM job)"
            )
            results = cur.fetchall()
        except Exception:
            logger.error("Could not retrieve jobs from database", exc_info=True)
        finally:
            cur.close()
        return results

    def get_processed_vulns(self):
        if not self.connection:
            raise Exception("Invalid connection")
        results = []
        try:
            cur = self.connection.cursor(cursor_factory=DictCursor)
            cur.execute(
                "SELECT pv.*, v.vuln_id FROM processed_vuln pv JOIN vulnerability v ON v._id = pv.fk_vulnerability"
            )
            results = cur.fetchall()
        except Exception:
            logger.error(
                "Could not retrieve processed vulnerabilities from database",
                exc_info=True,
            )
        finally:
            cur.close()
        return results

    def get_processed_vulns_not_in_job(
        self,
    ):  # entries in processed vuln excluding the ones already in the job table
        if not self.connection:
            raise Exception("Invalid connection")
        results = []
        try:
            cur = self.connection.cursor(cursor_factory=DictCursor)
            cur.execute(
                "SELECT pv._id, pv.repository, pv.versions, v.vuln_id FROM processed_vuln pv JOIN vulnerability v ON v._id = pv.fk_vulnerability LEFT JOIN job j ON pv._id = j.pv_id WHERE j.pv_id IS NULL"
            )
            results = cur.fetchall()
        except Exception:
            logger.error(
                "Could not retrieve processed vulnerabilities from database",
                exc_info=True,
            )
        finally:
            cur.close()
        return results

    def get_unprocessed_vulns(self):
        if not self.connection:
            raise Exception("Invalid connection")
        results = []
        try:
            cur = self.connection.cursor(cursor_factory=DictCursor)
            cur.execute(
                "SELECT _id, raw_record FROM vulnerability WHERE _id NOT IN ( SELECT fk_vulnerability FROM processed_vuln)"
            )
            results = cur.fetchall()
        except Exception:
            logger.error(
                "Could not retrieve unprocessed vulnerabilities from database",
                exc_info=True,
            )
        finally:
            cur.close()
        return results

    def save_processed_vuln(self, fk_vuln: int, repository: str, versions: str):
        if not self.connection:
            raise Exception("Invalid connection")
        try:
            cur = self.connection.cursor()
            cur.execute(
                "INSERT INTO processed_vuln (fk_vulnerability, repository,versions) VALUES (%s,%s,%s)",
                (fk_vuln, repository, versions),
            )
            self.connection.commit()
            cur.close()
        except Exception:
            logger.error(
                "Could not save processed vulnerability to database", exc_info=True
            )
            cur.close()

    def get_all_jobs(self):
        if not self.connection:
            raise Exception("Invalid connection")
        results = []
        try:
            cur = self.connection.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT * FROM job")
            results = cur.fetchall()
        except Exception:
            logger.error(
                "Could not retrieve jobs from database",
                exc_info=True,
            )
        finally:
            cur.close()
        return results

    def lookup_job_id(self, job_id: str):
        if not self.connection:
            raise Exception("Invalid connection")
        results = None
        try:
            cur = self.connection.cursor(cursor_factory=DictCursor)
            cur.execute("SELECT * FROM job WHERE _id = %s", (job_id,))
            results = cur.fetchone()
            self.connection.commit()
            logger.error(f"Job {job_id} retrieved correctly")
        except Exception:
            self.connection.rollback()
            logger.error("Could not lookup job in database", exc_info=True)
        finally:
            cur.close()
        return results

    def update_job(
        self,
        job_id: str,
        status: str,
        started_at: str = None,
        ended_at: str = None,
        results: str = None,
    ):
        if not self.connection:
            raise Exception("Invalid connection")

        try:
            cur = self.connection.cursor()

            if ended_at is None:
                cur.execute(
                    "UPDATE job SET status = %s, started_at = %s WHERE _id = %s",
                    (status, started_at, job_id),
                )
            else:
                cur.execute(
                    "UPDATE job SET status = %s, finished_at = %s, results = %s WHERE _id = %s",
                    (status, ended_at, results, job_id),
                )
            self.connection.commit()
            cur.close()
        except Exception:
            logger.error("Could not update job status in database", exc_info=True)
            cur.close()


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
