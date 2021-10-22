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

    def create_tables(self):
        self.create_linked_in_profiles_table()
        self.create_linked_in_contacts_table()

    def open_connection_to_db(self):
        try:
            connection_string = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
            connection = psycopg2.connect(connection_string)
            self.conn = connection
            log(log.INFO, "Connection to db is successfully opened:  <%s>", connection)
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

    def create_linked_in_contacts_table(self):
        """Check if DB exists, create table if it does not exist"""
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS contacts (
            id serial PRIMARY KEY NOT NULL,
            link TEXT NOT NULL,
            day DATE NOT NULL DEFAULT CURRENT_DATE
            );
            """
        )
        self.conn.commit()

    def get_profiles_with_empty_email(self):
        """Return list of profiles links where email field is empty"""
        self.cur.execute("SELECT link FROM profiles WHERE email IS NULL")
        list_of_links = self.cur.fetchall()
        if list_of_links is not None:
            return list_of_links

    def get_links_of_added_contacts(self):
        """Return list of contacts links who get connect invitation from bot"""
        self.cur.execute("SELECT link FROM contacts WHERE day IS NOT NULL")
        list_of_links = self.cur.fetchall()
        if list_of_links is not None:
            return list_of_links

    def get_number_of_contacts_added_today(self):
        """Return number of items created today"""
        self.cur.execute("SELECT count(id) FROM contacts WHERE day = CURRENT_DATE")
        number_of_contacts = self.cur.fetchone()
        return number_of_contacts

    def create_linked_in_profiles_table(self):
        """Check if DB exists, create table if it does not exist"""

        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS profiles (
            id serial PRIMARY KEY NOT NULL,
            link TEXT,
            name TEXT,
            headline TEXT,
            company TEXT,
            school TEXT,
            location TEXT,
            summary TEXT,
            image TEXT,
            email TEXT,
            phone TEXT,
            connected TEXT,
            birth TEXT,
            address TEXT,
            twitter TEXT,
            websites TEXT []
            );
        """
        )
        self.conn.commit()

    def update_profile_contact_info_data(self, data, link: str):
        """Update profile contact data.

        Parameters
        ---------
        data : tuple : (email, phone, connected, birth, address, twitter, websites) - all strings
        """
        profile_link = (link,)
        self.cur.execute(
            f"""
            UPDATE profiles SET (email, phone, connected, birth, address, twitter, websites) = (%s, %s, %s, %s, %s, %s, %s)
            WHERE link = "{profile_link[0]}";
            """,
            data,
        )
        self.conn.commit()

    def profile_is_already_scrapped(self, link: str):
        self.cur.execute("SELECT * FROM profiles WHERE link = %s", (link,))
        if self.cur.fetchone() is None:
            return False
        else:
            return True

    def contact_is_already_scrapped(self, link: str):
        log(log.INFO, "Check if link is in db: %s", link)
        self.cur.execute("SELECT * FROM contacts WHERE link = %s", (link,))
        if self.cur.fetchone() is None:
            return False
        else:
            return True

    def insert_profile_link(self, link: str):
        """Insert linkedin profile url into DB"""

        self.cur.execute(
            """
            INSERT INTO profiles(link) VALUES (%s)
            """,
            (link,),
        )
        self.conn.commit()
        log(
            log.INFO,
            "New profile link is added to DB: %s",
            link,
        )

    def insert_profile(self, data):
        """Inserts profile data into DB.

        Parameters
        ---------
        data : tuple : (link, name, headline, company, school, location, summary, image, email, phone, connected, birth, address, twitter, websites) - all strings
        """
        self.cur.execute(
            """
            INSERT INTO profiles(link, name, headline, company, school, location,
            summary, image, email, phone, connected, birth, address, twitter, websites )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            data,
        )
        self.conn.commit()

    def insert_contact(self, data):
        """Inserts contact data into DB.

        Parameters
        ---------
        data : tuple : (link,) - all strings
        """
        self.cur.execute(
            """
            INSERT INTO contacts(link)
            VALUES (%s)
            """,
            data,
        )
        self.conn.commit()

    def close_connection_to_db(self):
        try:
            if self.conn:
                self.conn.close()

        except Exception as error:
            log(log.ERROR, "Error during closing connection to db: [%s]", str(error))

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        log(log.INFO, "Close db cursor")
        self.close_cursor()
        log(log.INFO, "Close connection to db")
        self.close_connection_to_db()
