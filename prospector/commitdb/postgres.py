import psycopg2
from . import CommitDB


class PostgresCommitDB(CommitDB):
    def __init__(self):
        self.connect_string = ''
        self.connection_data = dict()
        self.connection = None

    def connect(self, connect_string=None):
        self.connect_string = connect_string.rstrip(";")
        self.connection_data = parse_connect_string(self.connect_string)
        print(self.connection_data)
        self.connection = psycopg2.connect(
            host = self.connection_data['host'],
            dbname = self.connection_data['db'],
            user = self.connection_data['uid'],
            password = self.connection_data['pwd'])
    
    def lookup(self, commit_obj):
        if not self.connection:
            raise Exception("Invalid connection")
        try:
            cur = self.connection.cursor()
            cur.execute("SELECT * FROM test")
            data = cur.fetchone()
        except:
            raise Exception("Could not lookup commit vector in database")

        return data
    
    def save(self, commit_obj):
        if not self.connection:
            raise Exception("Invalid connection")

        try:
            cur = self.connection.cursor()
            cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))
            self.connection.commit()
        except:
            raise Exception("Could not save commit vector to database")
        

    def reset():
        if not self.connection:
            raise Exception("Invalid connection")

        cur = self.connection.cursor()
        cur.execute("DROP TABLE IF EXISTS test;")
        cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
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
