import os
import mysql.connector
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


class DBUtils:
    def __init__(self, user, password, database, host="localhost", port=3306):
        """ Future work: Implement connection pooling """
        self.con = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )

    @classmethod
    def from_env(cls):
        """Create DBUtils using MYSQL_* variables from .env"""
        return cls(
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DB"),
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
        )

    def close(self):
        """ Close or release a connection back to the connection pool """
        self.con.close()
        self.con = None

    def execute(self, query):
        """ Execute a select query and returns the result as a dataframe """

        # Step 1: Create cursor
        rs = self.con.cursor()

        # Step 2: Execute the query
        rs.execute(query)

        # Step 3: Get the resulting rows and column names
        rows = rs.fetchall()
        cols = list(rs.column_names)

        # Step 4: Close the cursor
        rs.close()

        # Step 5: Return result
        return pd.DataFrame(rows, columns=cols)

    def insert_one(self, sql, val):
        """ Insert a single row """
        cursor = self.con.cursor()
        cursor.execute(sql, val)
        self.con.commit()
        cursor.close()

    def insert_many(self, sql, vals):
        """ Insert multiple rows """
        cursor = self.con.cursor()
        cursor.executemany(sql, vals)
        self.con.commit()
        cursor.close()