import psycopg2
from psycopg2.extras import NamedTupleCursor
from . import CommitDB
from datamodel.commit import Commit


class PostgresCommitDB(CommitDB):
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
            # TODO this returns all records, implement real query!
            cur.execute("SELECT * FROM commits")
            data = cur.fetchall()
            cur.close()
        except Exception as e:
            print(e)
            # raise Exception("Could not lookup commit vector in database")

        return data

    def save(self, commit_obj: Commit):
        if not self.connection:
            raise Exception("Invalid connection")

        try:
            cur = self.connection.cursor()

            # TODO sanitize inputs
            cur.execute(
                "INSERT INTO commits (id, repository, feature_1, feature_2) VALUES (%s, %s, %s, %s)",
                (
                    commit_obj.id,
                    commit_obj.repository,
                    commit_obj.feature_1,
                    commit_obj.feature_2,
                ),
            )
            self.connection.commit()
        except:
            raise Exception("Could not save commit vector to database")

    def reset(self):
        """
        Resets the database by dropping its tables and recreating them afresh.
        If the database does not exist, or any tables are missing, they
        are created.
        """

        if not self.connection:
            raise Exception("Invalid connection")

        self._create_table_commits()

    def _create_table_commits(self):
        """
        Input:
            sqlite3.connection: the connection with the database
        """
        if not self.connection:
            raise Exception("Invalid connection")

        cursor = self.connection.cursor()

        cursor.execute("DROP TABLE IF EXISTS commits;")
        cursor.execute(
            """CREATE TABLE commits (
            id varchar(40),
            repository varchar,
            feature_1 varchar,
            feature_2 varchar,
            timestamp text,
            message varchar,
            changed_files varchar,
            diff varchar,
            hunks varchar,
            commit_message_reference_content varchar,
            preprocessed_message varchar,
            preprocessed_diff varchar,
            preprocessed_changed_files varchar,
            preprocessed_commit_message_reference_content varchar,
            PRIMARY KEY (id, repository)
        )"""
        )

        cursor.execute("CREATE INDEX IF NOT EXISTS commit_index ON commits(id)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS repository_index ON commits(repository)"
        )
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS commit_repository_index ON commits(id, repository)"
        )
        self.connection.commit()

        cursor.close()
        return


def parse_connect_string(connect_string):
    # TODO convert to better connection string format
    # https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
    result = dict()
    connect_string = connect_string.rstrip(";")
    try:
        parsed_string = [e.split("=") for e in connect_string.split(";")]
        for k, v in parsed_string:
            result[k.lower()] = v
    except:
        raise Exception("Invalid connect string: " + connect_string)

    return dict(result)
