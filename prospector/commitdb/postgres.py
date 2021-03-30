import psycopg2
from psycopg2.extras import NamedTupleCursor
from . import CommitDB


class PostgresCommitDB(CommitDB):
    def __init__(self):
        self.connect_string = ''
        self.connection_data = dict()
        self.connection = None

    def connect(self, connect_string=None):
        self.connect_string = connect_string.rstrip(";")
        self.connection_data = parse_connect_string(self.connect_string)

        self.connection = psycopg2.connect(
            host = self.connection_data['host'],
            dbname = self.connection_data['db'],
            user = self.connection_data['uid'],
            password = self.connection_data['pwd'],
            cursor_factory=NamedTupleCursor)
    
    def lookup(self, commit_obj):
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
    
    def save(self, commit_obj):
        if not self.connection:
            raise Exception("Invalid connection")

        try:
            cur = self.connection.cursor()
            commit_id = commit_obj['id']
            repository = commit_obj['repository']
            feat_1 = "X"
            feat_2 = "Y"
            # TODO sanitize inputs
            cur.execute("INSERT INTO commits (hash, repository, feature_1, feature_2) VALUES (%s, %s, %s, %s)", (commit_id, repository, feat_1, feat_2))
            self.connection.commit()
        except:
            raise Exception("Could not save commit vector to database")
        

    def reset(self):
        if not self.connection:
            raise Exception("Invalid connection")

        cur = self.connection.cursor()
        cur.execute("DROP TABLE IF EXISTS commits;")
        cur.execute("""CREATE TABLE commits (
                        hash varchar(40),
                        repository varchar,
                        feature_1 varchar,
                        feature_2 varchar,
                        PRIMARY KEY (hash, repository)
                       )""")
        self.connection.commit()

def parse_connect_string(connect_string):
    # TODO convert to better connection string format
    # https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
    result = dict()
    connect_string = connect_string.rstrip(";")
    try:
        parsed_string = [ e.split('=') for e in connect_string.split(';') ]
        for k,v in parsed_string:
            result[k.lower()] = v
    except:
        raise Exception("Invalid connect string: " + connect_string)

    return dict(result)
