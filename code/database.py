"""Database creation

This file is used to create a database called fastchatdb which creates six tables
auth,server,message,image,Groups,privateKeyTable and grant some permissions to client

"""

import psycopg2
import sys

conn = psycopg2.connect(
        database=sys.argv[3],
        user=sys.argv[1],
        password=sys.argv[2],
        host='localhost',
        port='5432'
    )

cursor = conn.cursor()
cursor.execute('''SELECT 'CREATE DATABASE fastchatdb'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'fastchatdb')''')
conn.commit()

conn = psycopg2.connect(
        database='fastchatdb',
        user=sys.argv[1],
        password=sys.argv[2],
        host='localhost',
        port='5432'
    )
cursor = conn.cursor()
cursor.execute('''SELECT 'CREATE ROLE superserver SUPERUSER LOGIN PASSWORD "superserver@123" '
WHERE NOT EXISTS (SELECT * FROM pg_catalog.pg_user WHERE usename = 'superserver')  ''')
cursor.execute('''SELECT 'CREATE ROLE server LOGIN PASSWORD "server@fastchat" ' 
WHERE NOT EXISTS (SELECT * FROM pg_catalog.pg_user WHERE usename = 'server')  ''')
cursor.execute('''SELECT 'CREATE ROLE client LOGIN PASSWORD "Client@fastchat" '
WHERE NOT EXISTS (SELECT * FROM pg_catalog.pg_user WHERE usename = 'client')  ''')
cursor.execute('''CREATE TABLE IF NOT EXISTS auth(
            username TEXT NOT NULL PRIMARY KEY,
            password TEXT NOT NULL ,
            salt TEXT NOT NULL,
            publicKeyn TEXT NOT NULL,
            publicKeye integer NOT NULL
        )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS server(
    serverId integer NOT NULL ,
    clientId TEXT NOT NULL 
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS message(
    sender TEXT NOT NULL,
    reciever TEXT NOT NULL,
    message TEXT ,
    time TIMESTAMP
)
''')
cursor.execute('''CREATE TABLE IF NOT EXISTS image(
            sender TEXT NOT NULL,
            reciever TEXT NOT NULL,
            img BYTEA NOT NULL,
            time TIMESTAMP,
            displayed BOOL,
            imagenames TEXT NOT NULL
        )
''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Groups(
    group_name TEXT NOT NULL,
    participant TEXT NOT NULL,
    is_admin BOOL,
    id integer NOT NULL
)
''')
cursor.execute('''CREATE TABLE IF NOT EXISTS privateKeyTable(username TEXT NOT NULL,
    privateKeyn TEXT NOT NULL,
    privateKeye TEXT NOT NULL,
    privateKeyd TEXT NOT NULL,
    privateKeyp TEXT NOT NULL,
    privateKeyq TEXT NOT NULL
)''')
cursor.execute('''GRANT SELECT, INSERT ON auth TO client''')
cursor.execute('''GRANT SELECT, INSERT ON message TO client''')
cursor.execute('''GRANT SELECT, INSERT, UPDATE ON image TO client''')
cursor.execute('''GRANT INSERT ON privateKeyTable TO client''')
cursor.execute('''GRANT SELECT, INSERT, UPDATE, DELETE ON Groups TO client''')
cursor.execute('''GRANT SELECT, INSERT, UPDATE ON server TO server''')
conn.commit()





