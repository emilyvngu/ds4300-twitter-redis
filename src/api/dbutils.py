import os
import mysql.connector
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()

@contextmanager
def get_connection():
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
        autocommit=False
    )
    try:
        yield conn
    finally:
        conn.close()