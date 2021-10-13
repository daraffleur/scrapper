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
        return self.curr

    def create_linked_in_positions_table(self):
        """Check if DB exists, create table if it does not exist"""
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS linkedin_positions(
            id INTEGER PRIMARY KEY NOT NULL,
            position TEXT,
            company TEXT,
            location TEXT,
            details TEXT,
            date INT
            );
        """
        )
        self.conn.commit()

    def create_linked_in_profiles_table(self):
        """Check if DB exists, create table if it does not exist"""

        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS linkedin_profiles(
            id INTEGER PRIMARY KEY NOT NULL,
            full_name TEXT,
            description TEXT,
            location TEXT
            );
        """
        )
        self.conn.commit()

    def profile_data_is_duplicated(self, data):
        """Check if profile data is duplicate

        Parameters
        ---------
        data : tuple : (full_name, description, location) - all strings

        Returns : Boolean if duplicate
        """
        self.cur.execute(
            """
            SELECT *
            FROM linkedin_profiles
            WHERE (full_name = ?)
            AND (description = ?)
            AND (location = ?)
            ;
            """,
            data,
        )

        if self.cur.fetchone() is None:
            return False
        else:
            return True

    def positions_is_duplicated(self, data):
        """Check if data is duplicate

        Parameters
        ---------
        data : tuple : (position, company, location, details) - all strings

        Returns : Boolean if duplicate
        """
        # check DB for duplicate:
        self.cur.execute(
            """
            SELECT *
            FROM positions
            WHERE position = ?
            AND company = ?
            AND location = ?
            AND details = ?
            ;
            """,
            data,
        )

        if self.cur.fetchone() is None:
            return False
        else:
            return True

    def insert_position(self, data):
        """Inserts into DB.

        Parameters
        ---------
        data : tuple : (position, company, location, details) - all strings
        """
        self.cur.execute(
            """
            INSERT INTO linkedin_positions(position, company, location, details, date) VALUES (?, ?, ?, ?, date('now'))
            """,
            data,
        )
        self.conn.commit()

    def insert_profile(self, data):
        """Inserts profile data into DB.

        Parameters
        ---------
        data : tuple : (full_name, description, location) - all strings
        """
        self.cur.execute(
            """
            INSERT INTO linkedin_profiles(full_name, description, location) VALUES (?, ?, ?)
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
