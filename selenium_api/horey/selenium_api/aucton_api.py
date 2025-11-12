import datetime
from horey.async_orchestrator.async_orchestrator import AsyncOrchestrator
from horey.selenium_api.maauction import MAauction
from horey.selenium_api.mcsherryauction import Mcsherryauction
from horey.selenium_api.auction_event import AuctionEvent
from horey.selenium_api.lot import Lot
import sqlite3
from horey.h_logger import get_logger


logger = get_logger()


class AuctionAPI:
    def __init__(self):
        self.db_file_path = "/opt/horey/auctions.db"
        self.providers = [Mcsherryauction(), MAauction()]
        self.auction_events = None
        self.lots = None
        self.async_orchestrator = AsyncOrchestrator()

    def init_providers_from_db(self):
        """
        Init all providers

        :return:
        """

        map_providers = {}
        with sqlite3.connect(self.db_file_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM providers")
            records = cursor.fetchall()
            for auc_id, name in records:
                for provider in self.providers:
                    if provider.name == name:
                        provider.id = auc_id
                        map_providers[provider.id] = provider

        auction_events = self.init_auction_events_from_db()
        for auction_event in auction_events:
            map_providers[auction_event.provider_id].auction_events.append(auction_event)

        return self.providers

    def write_providers_to_db(self):
        """
        Write into DB.

        :return:
        """

        with sqlite3.connect(self.db_file_path) as conn:
            # Database operations can be performed here
            # For example, creating a table:
            cursor = conn.cursor()

            for provider in self.providers:
                cursor.execute(
                    "INSERT OR IGNORE INTO providers (name) VALUES (?)",
                    (provider.name,)
                )

    def provsion_db_providers_table(self):
        """
        Create table

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

    def write_auction_events_to_db(self):
        """
        Write into DB.

        :return:
        """

        raise DeprecationWarning("Old")

    def provision_db_auction_events_table(self):
        with sqlite3.connect(self.db_file_path) as conn:
            # Database operations can be performed here
            # For example, creating a table:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auction_events (
                    id INTEGER PRIMARY KEY ,
                    provider_id INTEGER REFERENCES providers(id) NOT NULL,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    start_time TEXT,
                    end_time TEXT,
                    address TEXT NOT NULL,
                    provinces TEXT NOT NULL
                )
            ''')
            conn.commit()  # Commit changes to the database
            logger.info(f"Database '{self.db_file_path}' created successfully with 'auction_events' table.")

    def write_lots_to_db(self):
        """
        Write into DB.

        :return:
        """

        raise DeprecationWarning()

    def provision_db_lots_table(self):
        with sqlite3.connect(self.db_file_path) as conn:
            # Database operations can be performed here
            # For example, creating a table:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lots(
                    id INTEGER PRIMARY KEY,
                    auction_event_id INTEGER REFERENCES auction_events(id) NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    interested BOOL,
                    current_max REAL,
                    my_max REAL,
                    admin_fee STRING,
                    raw_text STRING,
                    url TEXT NOT NULL UNIQUE,
                    image_url TEXT,
                    address TEXT,
                    province TEXT
                )
            ''')
            conn.commit()  # Commit changes to the database
            logger.info(f"Database '{self.db_file_path}' created successfully with 'lots' table.")

    def init_auction_events_from_db(self):
        """
        Init auction events and their lots

        :return:
        """
        self.auction_events = []
        with sqlite3.connect(self.db_file_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM auction_events")
            known_auction_event_lines = cursor.fetchall()
            for line in known_auction_event_lines:
                event = AuctionEvent()
                event.init_from_db_line(line)

                if not event.id:
                    raise NotImplementedError("DB ID was not init properly")
                self.auction_events.append(event)

        lots = self.init_lots_from_db()

        map_events = {auction_event.id: auction_event for auction_event in self.auction_events}

        for lot in lots:
            map_events[lot.auction_event_id].lots.append(lot)

        return self.auction_events

    def init_lots_from_db(self):
        self.lots = []
        with sqlite3.connect(self.db_file_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM lots")
            lots_lines = cursor.fetchall()
            for line in lots_lines:
                lot = Lot()
                lot.init_from_db_line(line)
                self.lots.append(lot)
        return self.lots

    def provision_tables(self):
        """
        Provision empty tables.

        :return:
        """

        self.provsion_db_providers_table()
        self.provision_db_auction_events_table()
        self.provision_db_lots_table()

    def update_auction_event(self, auction_event_id, end_time=None, last_update_time=None):
        """
        '{"horey_cached_type": "datetime", "value": "2025-10-28 15:00:00.000000"}'

        :param auction_event_id:
        :param end_time:
        :param last_update_time:
        :return:
        """

        with sqlite3.connect(self.db_file_path) as conn:
            cursor = conn.cursor()
            if end_time:
                sql_update_end_time = """
                UPDATE auction_events
                SET end_time = ?
                WHERE id = ?
                """
                new_time = '{"horey_cached_type": "datetime", "value": "' + end_time + '"}'
                cursor.execute(sql_update_end_time, (new_time, auction_event_id))

            if last_update_time:
                sql_update_last_update_time = """
                 UPDATE auction_events
                 SET last_update_time = ?
                 WHERE id = ?
                 """

                new_time = '{"horey_cached_type": "datetime", "value": "' + last_update_time + '"}'
                cursor.execute(sql_update_last_update_time, (new_time, auction_event_id))

    def update_info(self):
        """
        Magic

        :return:
        """

        for provider in self.init_providers_from_db():
            provider.connect()
            for auction_event in provider.auction_events:
                if auction_event.end_time is None:
                    print("Manually check and set the ending time using url")
                    format_string = "%Y-%m-%d %H:%M:%S.%f"
                    breakpoint()
                    #auction_event.end_time = datetime.datetime(2025, month=11, day=29, hour=9, minute=0, second=0)
                    #self.update_auction_event_end_time(auction_event.id, auction_event.end_time.strftime(format_string))

                    #sample: self.update_auction_event_end_time(auction_event.id, "2025-11-29 15:00:00.000000")
                if auction_event.finished:
                    continue

                provider.init_auction_event_lots(auction_event)

                self.update_db_auction_event(auction_event)

    def update_db_auction_event(self, auction_event: AuctionEvent):
        """
        Write to DB the new info.

        :param auction_event:
        :return:
        """

        for lot in auction_event.lots:
            self.upsert_db_lot(lot)

    def upsert_db_lot(self, lot: Lot):
        insert_sql = """
                    INSERT INTO lots 
                    (auction_event_id, name, description, interested, current_max, my_max, admin_fee, raw_text, url, image_url, address, province)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """

        update_sql = """
            UPDATE lots
            SET 
                auction_event_id = ?,
                name = ?,
                description = ?,
                interested = ?,
                current_max = ?,
                my_max = ?,
                admin_fee = ?,
                raw_text = ?,
                url = ?,
                image_url = ?,
                address = ?,
                province = ?
            WHERE
                id = ?"""

        data_tuple = lot.generate_db_tuple()

        with sqlite3.connect(self.db_file_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")

            if lot.id is not None:
                cursor.execute(update_sql, data_tuple + (lot.id,))
            else:
                cursor.execute(insert_sql, data_tuple)

            conn.commit()

    def print_coming_auction(self):
        """
        Magic

        :return:
        """

        events = self.init_auction_events_from_db()
        by_date = {}
        for event in events:
            if event.finished:
                continue

            by_date[event.end_time] = event

        for auction_event_date in sorted(by_date):
            if not by_date[auction_event_date].provinces:
                breakpoint()
                logger.error("something went wrong")

            if "manitoba" not in by_date[auction_event_date].provinces:
                continue
            by_date[auction_event_date].print_interesting_information()
            breakpoint()

    def generate_auction_event_reports(self):
        """
        Magic

        :return:
        """
        reports = []
        events = self.init_auction_events_from_db()
        providers_by_id = {provider.id: provider for provider in self.init_providers_from_db()}
        by_date = {}
        for event in events:
            if event.finished:
                continue

            by_date[event.end_time] = event

        for auction_event_date in sorted(by_date):
            report = AuctionEventReport()
            report.auction_event = by_date[auction_event_date]
            report.provider = providers_by_id[report.auction_event.provider_id]
            reports.append(report)

        return reports

    def update_info_provider_auction_events(self, provider_id, asynchronous=False):
        if asynchronous:
            return self.async_orchestrator.start_task_from_function(self.update_info_provider_auction_events_asynchronous, provider_id)

        self.update_info_provider_auction_events_asynchronous(provider_id)

    def update_info_provider_auction_events_asynchronous(self, provider_id):
        breakpoint()
        self.init_providers_from_db()
        known_auction_events = self.init_auction_events_from_db()
        known_auction_event_urls = [known_auction_event.url for known_auction_event in known_auction_events if provider_id == known_auction_event.provider_id]
        sql = """
            INSERT INTO auction_events 
            (provider_id, name, description, url, start_time, end_time, address, provinces, last_update_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

        with sqlite3.connect(self.db_file_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")

            for provider in self.providers:
                if provider.id != provider_id:
                    continue
                auction_events = provider.init_auction_events()
                for auction_event in auction_events:
                    if auction_event.url in known_auction_event_urls:
                        continue

                    base_tuple = auction_event.generate_db_tuple()
                    data_tuple = (provider.id,) + base_tuple
                    cursor.execute(sql, data_tuple)
                    conn.commit()

    def update_info_auction_event(self, auction_event_id, asynchronous=False):
        if asynchronous:
            return self.async_orchestrator.start_task_from_function(self.update_info_auction_event_async, auction_event_id)

        self.update_info_auction_event_async(auction_event_id)

    def update_info_auction_event_async(self, auction_event_id):
        logger.info(f"Started auction_event_id with {auction_event_id}")

        self.init_providers_from_db()
        self.init_auction_events_from_db()

        known_lots = [lot for lot in self.init_lots_from_db() if lot.auction_event_id == auction_event_id]
        known_lot_urls = [known_lot.url for known_lot in known_lots]
        known_lot_auction_events = set([known_lot.auction_event_id for known_lot in known_lots])
        for provider in self.providers:
            for auction_event in self.auction_events:
                if auction_event.id != auction_event_id:
                    continue

                if auction_event.id in known_lot_auction_events:
                    continue

                for lot in provider.init_auction_event_lots(auction_event):
                    if lot.url in known_lot_urls:
                        continue
                    self.upsert_db_lot(lot)

                format_string = "%Y-%m-%d %H:%M:%S.%f"
                breakpoint()
                now = datetime.datetime.now(tz=datetime.timezone.utc)
                self.update_auction_event(auction_event.id, last_update_time=now.strftime(format_string))
                break


class AuctionEventReport:
    def __init__(self):
        self.provider = None
        self.auction_event = None

    @property
    def fetch_data_button_text(self):
        return f"{self.provider.name} {self.auction_event.end_time.strftime('%d/%m')}"

    @property
    def timestamp_text(self):
        return self.auction_event.end_time.strftime("%d/%m/%Y %H:%M")

    @property
    def provider_name(self):
        return self.provider.name

    @property
    def str_provider_id(self):
        return str(self.provider.id)

    @property
    def str_auction_event_id(self):
        return str(self.auction_event.id)

