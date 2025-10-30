from horey.selenium_api.maauction import MAauction
from horey.selenium_api.mcsherryauction import Mcsherryauction
from horey.selenium_api.auction_event import AuctionEvent
import sqlite3
from horey.h_logger import get_logger

logger = get_logger()


class AuctionAPI():
    def __init__(self):
        self.db_file_path = "/opt/horey/auctions.db"
        self.providers = [MAauction()]

    def init_providers(self):
        """
        Init all providers

        :return:
        """

        providers = []
        with sqlite3.connect(self.db_file_path) as conn:
            # Database operations can be performed here
            # For example, creating a table:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM providers")
            records = cursor.fetchall()
            for auc_id, name in records:
                for provider in self.providers:
                    if provider.name == name:
                        provider.id = auc_id
        return providers

    def write_providers_to_db(self):
        """
        Write into DB.

        :return:
        """

        with sqlite3.connect(self.db_file_path) as conn:
            # Database operations can be performed here
            # For example, creating a table:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS providers (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                )
            ''')
            conn.commit()  # Commit changes to the database
            logger.info(f"Database '{self.db_file_path}' created successfully with 'providers' table.")

            for provider in self.providers:
                cursor.execute(
                    "INSERT OR IGNORE INTO providers (name) VALUES (?)",
                    (provider.name,)
                )

    def write_auction_events_to_db(self):
        """
        Write into DB.

        :return:
        """

        self.provision_db_auction_events_table()

        known_auction_events = self.load_auction_events_from_db()
        known_auction_event_links = [known_auction_event.link for known_auction_event in known_auction_events]
        sql = """
            INSERT INTO auction_events 
            (provider_id, name, description, link, start_time, end_time, address, provinces)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
        with sqlite3.connect(self.db_file_path) as conn:
            # Database operations can be performed here
            # For example, creating a table:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")

            for provider in self.providers:
                auction_events = provider.init_auction_events()
                for auction_event in auction_events:
                    if auction_event.link in known_auction_event_links:
                        continue
                    breakpoint()
                    base_tuple = auction_event.generate_db_tuple()
                    data_tuple = (provider.id,) + base_tuple
                    cursor.execute(sql, data_tuple)
                    conn.commit()

    def provision_db_auction_events_table(self):
        with sqlite3.connect(self.db_file_path) as conn:
            # Database operations can be performed here
            # For example, creating a table:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auction_events (
                    id INTEGER PRIMARY KEY,
                    provider_id INTEGER REFERENCES providers(id),
                    name TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    link TEXT NOT NULL UNIQUE,
                    start_time TEXT,
                    end_time TEXT,
                    address TEXT NOT NULL,
                    provinces TEXT NOT NULL
                )
            ''')
            conn.commit()  # Commit changes to the database
            logger.info(f"Database '{self.db_file_path}' created successfully with 'auction_events' table.")

    def provision_db_lot(self):
        try:
            with sqlite3.connect("my_database.db") as conn:
                # Database operations can be performed here
                # For example, creating a table:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS providers (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT NOT NULL,
                        interested BOOL,
                        current_max REAL,
                        my_max REAL,
                        admin_fee STRING,
                        extras STRING
                    )
                ''')
                conn.commit()  # Commit changes to the database
                print("Database 'my_database.db' created successfully with 'users' table.")

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

    def load_auction_events_from_db(self):
        ret = []
        with sqlite3.connect(self.db_file_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM auction_events")
            known_auction_event_lines = cursor.fetchall()
            for line in known_auction_event_lines:
                event = AuctionEvent()
                event.init_from_db_line(line)
                ret.append(event)
        return ret

