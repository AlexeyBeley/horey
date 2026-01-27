import datetime
import time

from horey.async_orchestrator.async_orchestrator import AsyncOrchestrator
from horey.selenium_api.maauction import MAauction
from horey.selenium_api.mcsherryauction import Mcsherryauction
from horey.selenium_api.auction_event import AuctionEvent
from horey.selenium_api.pennerauction import Pennerauction
from horey.selenium_api.mcdougallauction import Mcdougallauction
from horey.selenium_api.kayesauction import Kayesauction
from horey.selenium_api.lot import Lot
import sqlite3
from horey.h_logger import get_logger

logger = get_logger()


class AuctionAPI:
    def __init__(self):
        self.db_file_path = "/opt/horey/auctions.db"
        self.providers = [Mcsherryauction(), MAauction(), Pennerauction(), Mcdougallauction(), Kayesauction()]
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

    def add_provider(self, provider):
        """
        Create table

        :return:
        """
        insert_sql = """
                    INSERT INTO providers 
                    (name)
                    VALUES (?)
                    """

        with sqlite3.connect(self.db_file_path) as conn:
            # Database operations can be performed here
            # For example, creating a table:
            cursor = conn.cursor()
            cursor.execute(insert_sql, [provider.name])
            conn.commit()
        logger.info(f"Database '{self.db_file_path}' added {provider.name} to 'providers' table.")


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
        """
        DB lots_table

        :return:
        """

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
                    starting_bid REAL NOT NULL,
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

    def upsert_db_auction_event(self, auction_event: AuctionEvent):
        """
        Update or insert auction event.

        :param auction_event:
        :return:
        """

        if auction_event.id is not None:
            if auction_event.end_time is not None:
                format_string = "%Y-%m-%d %H:%M:%S.%f"
                return self.update_auction_event(auction_event.id, end_time=auction_event.end_time.strftime(format_string))
            return True

        sql = """
            INSERT INTO auction_events 
            (provider_id, name, description, url, start_time, end_time, address, provinces, last_update_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

        with sqlite3.connect(self.db_file_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")

            base_tuple = auction_event.generate_db_tuple()
            data_tuple = (auction_event.provider_id,) + base_tuple
            try:
                cursor.execute(sql, data_tuple)
                conn.commit()
            except Exception as inst_err:
                logger.exception(inst_err)
                if "UNIQUE constraint" in repr(inst_err):
                    logger.error(f"Data is not unique: {data_tuple}")
                else:
                    logger.error(f"Unknown error with data: {data_tuple}")
                breakpoint()
                # for x in known_auction_events: print(x.id, x.name, x.url)
                # url = 'https://www.jardineauctioneers.com/auctions/24895-45th-annual-fredericton-sports-investment-auction?filter=(auction_ring_id:1200)'
                # self.update_auction_event(23, url=url)
                raise

        return True

    def update_auction_event(self, auction_event_id, end_time=None, start_time = None, last_update_time=None, url=None):
        """
        self.update_auction_event(139, start_time="2026-01-29 10:00:00.000000")
        '{"horey_cached_type": "datetime", "value": "2025-10-28 15:00:00.000000"}'

        :param start_time:
        :param url:
        :param auction_event_id:
        :param end_time:
        :param last_update_time:
        :return:
        """

        logger.info(f"Updating auction event: {auction_event_id}")

        with sqlite3.connect(self.db_file_path) as conn:
            cursor = conn.cursor()
            if start_time:
                sql_update_start_time = """
                UPDATE auction_events
                SET start_time = ?
                WHERE id = ?
                """
                new_time = '{"horey_cached_type": "datetime", "value": "' + start_time + '"}'
                cursor.execute(sql_update_start_time, (new_time, auction_event_id))

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

            if url:
                sql_update_url = """
                 UPDATE auction_events
                 SET url = ?
                 WHERE id = ?
                 """

                cursor.execute(sql_update_url, (url, auction_event_id))

    def update_db_auction_event(self, auction_event: AuctionEvent):
        """
        Write to DB the new info.

        :param auction_event:
        :return:
        """

        with sqlite3.connect(self.db_file_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            for lot in auction_event.lots:
                self.upsert_db_lot(conn, cursor, lot)

    def upsert_db_lot(self, conn: sqlite3.Connection, cursor: sqlite3.Cursor, lot: Lot):
        logger.info(f"Upserting Lot to DB: {lot.name}")
        insert_sql = """
                    INSERT INTO lots 
                    (auction_event_id, name, description, interested, starting_bid, current_max, my_max, admin_fee, raw_text, url, image_url, address, province)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """

        update_sql = """
            UPDATE lots
            SET 
                auction_event_id = ?,
                name = ?,
                description = ?,
                interested = ?,
                starting_bid = ?,
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

        try:
                if lot.id is not None:
                    cursor.execute(update_sql, data_tuple + (lot.id,))
                else:
                    try:
                        cursor.execute(insert_sql, data_tuple)
                    except Exception:
                        breakpoint()
                conn.commit()
        except sqlite3.OperationalError as e:
            if "unable to open database file" in str(e):
                logger.error(f"Database file access error: {self.db_file_path}")
                breakpoint()
                raise
            else:
                raise
        except Exception as inst_error:
            logger.exception(f"Error: {repr(inst_error)} inserting: {data_tuple}")
            raise

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
            # self.update_auction_event(143, start_time="2026-01-29 10:00:00.000000")
            logger.info(f"Checking event: {event.id}")

            try:
                event.finished

            except Exception:
                breakpoint()
                # self.update_auction_event(event.id, end_time="2026-01-23 10:00:00.000000")

            if event.finished:
                continue

            if event.end_time:
                by_date[event.end_time] = event
            else:
                by_date[event.start_time] = event

        for auction_event_date in sorted(by_date):
            report = AuctionEventReport()
            report.auction_event = by_date[auction_event_date]
            report.provider = providers_by_id[report.auction_event.provider_id]
            reports.append(report)

        known_provider_ids = {report.provider.id for report in reports}
        for provider in self.providers:
            if provider.id not in known_provider_ids:
                report = AuctionEventReport()
                report.provider = provider
                reports.append(report)

        return reports

    def update_info_provider_auction_events(self, provider_id, asynchronous=False):
        if asynchronous:
            task_name = f"update_info_provider_auction_events_asynchronous->{provider_id}"
            try:
                task = self.async_orchestrator.start_task_from_function(
                    self.update_info_provider_auction_events_asynchronous, provider_id, task_name=task_name)
            except self.async_orchestrator.ExistingTaskID:
                if self.async_orchestrator.tasks[task_name].finished:
                    del self.async_orchestrator.tasks[task_name]
                    task = self.async_orchestrator.start_task_from_function(
                        self.update_info_provider_auction_events_asynchronous, provider_id, task_name=task_name)
                    logger.info(f"Started {task_name}")
                else:
                    logger.info(f"Updating already in progress: provider_id {provider_id}")
                    task = self.async_orchestrator.tasks[task_name]
            return task

        self.update_info_provider_auction_events_asynchronous(provider_id)

    def init_provider_from_db(self, provider_id=None, provider_name=None):
        provider_id = int(provider_id) if provider_id is not None else None
        self.init_providers_from_db()
        for provider in self.providers:
            if provider_id is not None and provider.id == provider_id:
                break
            if provider_name is not None and provider.name == provider_name:
                break
        else:
            raise ValueError(f"Was not able to find provider {provider_id=}")

        self.init_auction_events_from_db()
        provider.auction_events = [self.init_auction_event_from_db(auction_event.id) for auction_event in
                                   self.auction_events if auction_event.provider_id == provider.id]
        return provider

    def update_info_provider_auction_events_asynchronous(self, provider_id):
        provider = self.init_provider_from_db(provider_id=provider_id)

        known_auction_events_by_url= {auction_event.url: auction_event  for auction_event in provider.auction_events}

        new_auction_events = provider.init_auction_events()
        if new_auction_events is None:
            return None

        for auction_event in new_auction_events:
            auction_event.provider_id = provider.id

            try:
                auction_event.id = known_auction_events_by_url[auction_event.url].id
            except KeyError:
                pass

            self.upsert_db_auction_event(auction_event)

        return None

    def update_info_auction_event(self, auction_event_id, asynchronous=False):
        if asynchronous:
            seconds_wait = 60
            task_name = f"update_info_auction_event->{auction_event_id}"
            try:
                task = self.async_orchestrator.start_task_from_function(self.update_info_auction_event_async,
                                                                        auction_event_id, task_name=task_name)

                logger.info(f"Started update_info_auction_event->{auction_event_id}")
            except self.async_orchestrator.ExistingTaskID:
                if self.async_orchestrator.tasks[task_name].finished:
                    del self.async_orchestrator.tasks[task_name]
                    task = self.async_orchestrator.start_task_from_function(self.update_info_auction_event_async,
                                                                            auction_event_id, task_name=task_name)
                    logger.info(f"Started update_info_auction_event->{auction_event_id}")
                else:
                    logger.info(f"Updating already in progress: auction_event {auction_event_id}")
                    task = self.async_orchestrator.tasks[task_name]

            logger.info(f"Starting waiting loop in update_info_auction_event->{auction_event_id}")
            for i in range(seconds_wait):
                if not task.finished:
                    logger.info(f"Update not yet finished, going to sleep {i}/{seconds_wait}")
                    time.sleep(1)
                    continue

                logger.info(f"Update finished, checking status")

                if task.exception:
                    return f"Update failed with exception {repr(task.exception)}"

                if task.exit_code != 0:
                    return f"Update failed with exit code {repr(task.exit_code)}"

                return f"Successfully updated update_info_auction_event->{auction_event_id}"

            return f"Started updating auction_event info and after {seconds_wait} seconds still running: {auction_event_id=}"

        self.update_info_auction_event_async(auction_event_id)

    def update_info_auction_event_async(self, auction_event_id):
        logger.info(f"Started update info for auction_event_id {auction_event_id}")

        auction_event = self.init_auction_event_from_db(auction_event_id)
        self.init_providers_from_db()

        for provider in self.providers:
            if auction_event.provider_id == provider.id:
                break
        else:
            raise RuntimeError(f"Was not able to find {auction_event.provider_id=} in the DB")

        logger.info(f"Updating {auction_event_id=} {auction_event.provider_id=}")

        old_lots_by_url = {lot.url: lot for lot in auction_event.lots}
        new_lots_by_url = {lot.url: lot for lot in provider.init_auction_event_lots(auction_event)}

        with sqlite3.connect(self.db_file_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            for lot in new_lots_by_url.values():
                self.upsert_db_lot(conn, cursor, lot)

            for lot_url, lot in old_lots_by_url.items():
                if lot_url not in new_lots_by_url:
                    self.delete_db_lot(conn, cursor, lot)

        format_string = "%Y-%m-%d %H:%M:%S.%f"
        now = datetime.datetime.now(tz=datetime.timezone.utc)

        self.update_auction_event(auction_event.id, last_update_time=now.strftime(format_string))

    def delete_auction_event_with_lots(self, auction_event_id):
        auction_event = self.init_auction_event_from_db(auction_event_id)
        with sqlite3.connect(self.db_file_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            for lot in auction_event.lots:
                self.delete_db_lot(conn, cursor, lot)
        self.delete_db_auction_event(auction_event)

    def delete_db_lot(self, conn: sqlite3.Connection, cursor: sqlite3.Cursor, lot: Lot):
        table_name = 'lots'
        delete_query = f"DELETE FROM {table_name} WHERE id = ?"

        try:
            cursor.execute(delete_query, (lot.id,))
            conn.commit()
        except Exception as inst_err:
            logger.exception(inst_err)
            breakpoint()
            raise

    def delete_db_auction_event(self, auction_event: AuctionEvent):
        table_name = 'auction_events'
        delete_query = f"DELETE FROM {table_name} WHERE id = ?"
        with sqlite3.connect(self.db_file_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(delete_query, (auction_event.id,))
                conn.commit()
            except Exception as inst_err:
                logger.exception(inst_err)
                breakpoint()
                raise

    def init_auction_event_from_db(self, auction_event_id) -> AuctionEvent:
        auction_event_id = int(auction_event_id)
        self.init_auction_events_from_db()

        for auction_event in self.auction_events:
            if auction_event.id == auction_event_id:
                self.init_lots_from_db()
                auction_event.lots = [lot for lot in self.lots if lot.auction_event_id == auction_event_id]
                return auction_event
        raise ValueError(f"Was not able to find {auction_event_id=}")

    def auction_event_manual_update(self):
        self.init_auction_events_from_db()
        for auction_event in self.auction_events:
            print(f"{auction_event.id} - name: {auction_event.name} - {auction_event.end_time} - {auction_event.url}")
        breakpoint()
        auction_event_id = 99
        self.update_auction_event(auction_event_id, end_time="2025-11-25 20:00:00.000000")

    def add_column_after_column(self):
        """
            id INTEGER PRIMARY KEY,
            auction_event_id INTEGER REFERENCES auction_events(id) NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            interested BOOL,
            starting_bid REAL NOT NULL,
            current_max REAL,
            my_max REAL,
            admin_fee STRING,
            raw_text STRING,
            url TEXT NOT NULL UNIQUE,
            image_url TEXT,
            address TEXT,
            province TEXT

        :return:
        """
        breakpoint()
        self.raw_sqlite_command("ALTER TABLE lots RENAME TO _lots_old;")

        self.provision_db_lots_table()
        query = """
        INSERT INTO lots (
        id,
        auction_event_id,
        name,
        description,
        interested,
        starting_bid,
        current_max,
        my_max,
        admin_fee,
        raw_text,
        url,
        image_url,
        address,
        province
        )
        SELECT
        id,
        auction_event_id,
        name,
        description,
        interested,
        1 AS starting_bid,
        current_max,
        my_max,
        admin_fee,
        raw_text,
        url,
        image_url,
        address,
        province
        FROM
        _lots_old;
        """

        self.raw_sqlite_command(query)

        self.raw_sqlite_command("DROP TABLE _lots_old;")

    def raw_sqlite_command(self, query, *args, **kwargs):
        """
        Command
        :return:
        """

        with sqlite3.connect(self.db_file_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, *args, **kwargs)
                conn.commit()
            except Exception as inst_err:
                logger.exception(inst_err)
                breakpoint()
                raise

    def delete_providers_auction_events(self, provider):
        """
        Delete all auction events of the provider.

        :param provider:
        :return:
        """

        breakpoint()
        return 0

        provider = self.init_provider_from_db(provider_name=provider.name)
        for auction_event in provider.auction_events:
            self.raw_sqlite_command(f"DELETE FROM auction_events WHERE id = ?",
                    (auction_event.id,))
            logger.info(f"Deleted {auction_event.name=}")
        logger.info(f"Deleted total {len(provider.auction_events)} auction events")


class AuctionEventReport:
    def __init__(self):
        self.provider = None
        self.auction_event = None

    @property
    def load_data_button_text(self):
        if self.auction_event.end_time:
            return f"[{self.auction_event.id}] {self.provider.name} {self.auction_event.end_time.strftime('%d/%m')}"
        return f"[{self.auction_event.id}] {self.provider.name} {self.auction_event.start_time.strftime('%d/%m')}"


    @property
    def timestamp_text(self):
        if self.auction_event.end_time:
            return self.auction_event.end_time.strftime("%d/%m/%Y %H:%M")
        return self.auction_event.start_time.strftime("%d/%m/%Y %H:%M")

    @property
    def provider_name(self):
        return self.provider.name

    @property
    def str_provider_id(self):
        return str(self.provider.id)

    @property
    def str_auction_event_id(self):
        return str(self.auction_event.id)

