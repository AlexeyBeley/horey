from horey.selenium_api.maauction import MAauction
from horey.selenium_api.mcsherryauction import Mcsherryauction
import sqlite3


class AuctionAPI():
    def __init__(self):
        self.db_file_path = "/opt/horey/auctions.db"
        self.providers = [MAauction(), Mcsherryauction()]

    def init_all_lots(self):
        """
        Init all lots

        :return:
        """
        lots = []
        for provider in self.providers:
            lots += provider.init_all_lots()

    def init_all_auctions(self):
        """
        Init all auctions.

        :return:
        """

        auctions = []
        for provider in self.providers:
            auctions += provider.init_all_auctions()
        breakpoint()

    def init_all_providers(self):
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
            breakpoint()

    def provision_db_providers(self):
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
            print("Database 'my_database.db' created successfully with 'users' table.")

            for provider in self.providers:
                cursor.execute(
                    "INSERT OR IGNORE INTO providers (name) VALUES (?)",
                    (provider.name,)
                )

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
