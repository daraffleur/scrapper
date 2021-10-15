import os
import psycopg2
from dotenv import load_dotenv
from app.logger import log


load_dotenv()


DB_HOST = "127.0.0.1"
# DB_HOST = os.environ.get("POSTGRES_SERVER")
DB_PORT = os.environ.get("POSTGRES_REMOTE_PORT")
DB_NAME = os.environ.get("POSTGRES_DB")
DB_USER = os.environ.get("POSTGRES_USER")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD")


class Database:
    def __init__(self):
        self.conn = None
        self.cur = None

        self.open_connection_to_db()
        self.create_cursor()

    def open_connection_to_db(self):
        try:
            connection_string = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
            connection = psycopg2.connect(connection_string)
            self.conn = connection
            log(log.INFO, "Connection to db is successfully opened:  <%s>", connection)
            # return connection
        except Exception as error:
            log(
                log.ERROR,
                "Error has occured during connection to database: [%s]",
                str(error),
            )

    def get_connection(self):
        return self.conn

    def close(self):
        """Close DB connection"""
        self.conn.close()

    def create_cursor(self):
        cur = self.conn.cursor()
        log(log.INFO, "DB cursor is successfully creates:  <%s>", cur)
        self.cur = cur

    def get_cursor(self):
        return self.cur

    def close_cursor(self):
        try:
            if self.cur:
                self.cur.close()

        except Exception as error:
            log(log.ERROR, "Error during closing cursor connection: [%s]", str(error))

    def create_linked_in_profiles_table(self):
        """Check if DB exists, create table if it does not exist"""

        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS profiles (
            id serial PRIMARY KEY NOT NULL,
            link TEXT,
            name TEXT,
            description TEXT,
            location TEXT
            );
        """
        )
        self.conn.commit()

    def profile_is_already_scrapped(self, link: str):
        self.cur.execute("SELECT * FROM profiles WHERE link = %s", (link,))
        if self.cur.fetchone() is None:
            return False
        else:
            return True

    def profile_data_is_duplicated(self, data):
        """Check if profile data is duplicate

        Parameters
        ---------
        data : tuple : (name, description, location) - all strings

        Returns : Boolean if duplicate
        """
        self.cur.execute(
            """
            SELECT *
            FROM profiles
            WHERE name = ?
            AND "description" = ?
            AND "location" = ?
            ;
            """,
            data,
        )

        if self.cur.fetchone() is None:
            return False
        else:
            return True

    def insert_profile(self, data):
        """Inserts profile data into DB.

        Parameters
        ---------
        data : tuple : (link, full_name, description, location) - all strings
        """
        self.cur.execute(
            """
            INSERT INTO profiles(link, name, description, location) VALUES (%s, %s, %s, %s)
            """,
            data,
        )
        self.conn.commit()

    def close_connection_to_db(self, connection):
        try:
            if connection:
                connection.close()

        except Exception as error:
            log(log.ERROR, "Error during closing connection to db: [%s]", str(error))
