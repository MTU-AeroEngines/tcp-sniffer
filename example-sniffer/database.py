import os
import sqlite3

DB_PATH = 'database.db'

db_exists = os.path.exists(DB_PATH)
db = sqlite3.connect(DB_PATH, check_same_thread=False, isolation_level=None)
cur = db.cursor()
if not db_exists:
    cur.execute('''CREATE TABLE sessions (
                    session_id TEXT,
                    PRIMARY KEY (session_id)
                )''')
    # direction: 0 - from client to the server
    #            1 - from server to the client
    cur.execute('''CREATE TABLE data (
                    session_id TEXT,
                    timestamp UNSIGNED BIGINT,
                    direction INT NOT NULL,
                    data BLOB NOT NULL,
                    PRIMARY KEY (session_id, timestamp)''')
    cur.close()
