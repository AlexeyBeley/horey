import datetime
import shutil
import sqlite3
from pathlib import Path
import zipfile

import requests
from horey.free_stuff_api.free_stuff_api_configuration_policy import FreeStuffAPIConfigurationPolicy

from horey.aws_api.aws_api import AWSAPI
from horey.h_logger import get_logger
from horey.common_utils.free_item import FreeItem
from horey.facebook_api.facebook_api import FacebookAPI
from horey.infrastructure_api.aws_lambda_api import AWSLambdaAPIConfigurationPolicy, AWSLambdaAPI
from horey.infrastructure_api.db_api import DBAPI
from horey.infrastructure_api.db_api_configuration_policy import DBAPIConfigurationPolicy
from horey.infrastructure_api.environment_api import EnvironmentAPIConfigurationPolicy, EnvironmentAPI
from horey.selenium_api.selenium_api import SeleniumAPI
from horey.free_stuff_api.platform import Platform

logger = get_logger()

class FreeStuffAPI:
    def __init__(self, configuration: FreeStuffAPIConfigurationPolicy = None):
        self.configuration = configuration
        self.selenium_api = SeleniumAPI(chromedriver_path= self.configuration.chromedriver_path,
                                                                   chrome_path=self.configuration.chrome_path)
        self.platforms = None
        self.init_platforms()
        self._db_api = None
        self._environment_api = None
        self._aws_lambda_api = None

    def init_platforms(self):
        """
        Init platforms from DB
        :return:
        """

        platform_apis = [FacebookAPI(selenium_api=self.selenium_api)]

        with sqlite3.connect(self.configuration.db_file_path) as conn:
            cursor = conn.cursor()
            response = cursor.execute("select * from tbl_platforms")
            lines = response.fetchall()
            for line in lines:
                platform_id, platform_name = line
                for platform_api in platform_apis:
                    if platform_api.NAME == platform_name:
                        platform = Platform(platform_id, platform_name, api=platform_api)
                        self.init_platform_free_items(platform)
                        if self.platforms is None:
                            self.platforms = []
                        self.platforms.append(platform)
                        break

    def init_platform_free_items(self, platform: Platform):
        """
        Init platform free items from DB
        :param platform:
        :return:
        """

        with sqlite3.connect(self.configuration.db_file_path) as conn:
            cursor = conn.cursor()
            response = cursor.execute("select * from tbl_free_items where platform_id=?", (platform.id, ))
            lines = response.fetchall()
            platform.free_items = {}
            for line in lines:
                (
                    _,
                    _,
                    free_item_name,
                    free_item_description,
                    free_item_url,
                    free_item_image_url,
                    free_item_address,
                    ingestion_time
                ) = line

                ingestion_time = datetime.datetime.fromtimestamp(ingestion_time, tz=datetime.timezone.utc)
                free_item = FreeItem(free_item_name, free_item_url, image_url=free_item_image_url, description=free_item_description,  address=free_item_address, ingestion_time=ingestion_time)
                platform.free_items[free_item.url] = free_item

    @property
    def environment_api(self):
        """
        Environment API
        :return:
        """

        if self._environment_api is None:
            config = EnvironmentAPIConfigurationPolicy()
            config.region = self.configuration.region
            config.project_name = "hfrs"
            config.environment_name = "qa"
            config.environment_level = "development"
            config.project_name_abbr = "hfrs"
            self._environment_api = EnvironmentAPI(config, AWSAPI())
        return self._environment_api

    @property
    def db_api(self):
        """
        DB API
        :return:
        """
        if self._db_api is None:
            configuration = DBAPIConfigurationPolicy()
            self._db_api = DBAPI(configuration, self.environment_api)
        return self._db_api

    @property
    def aws_lambda_api(self):
        """
        DB API
        :return:
        """

        if self._aws_lambda_api is None:
            configuration = AWSLambdaAPIConfigurationPolicy()
            # todo: rename
            configuration.lambda_name = "test_selenium"
            configuration.lambda_timeout = 600
            configuration.lambda_memory_size = 2048
            # configuration.architecture = "arm64"
            self._aws_lambda_api = AWSLambdaAPI(configuration, self.environment_api)
            self._aws_lambda_api.build_api.horey_git_api.configuration.git_directory_path = self.configuration.horey_directory_path.parent
            self._aws_lambda_api.build_api.prepare_docker_image_build_directory = lambda x, y: self._aws_lambda_api.build_api.prepare_docker_image_horey_package_build_directory(x, "free_stuff_api", y)
            self._aws_lambda_api.build_api.prepare_docker_image_build_directory_callback = self.prepare_docker_image_build_directory_callback

        return self._aws_lambda_api

    def prepare_docker_image_build_directory_callback(self, docker_build_directory):
        """
        Prepare the dir.

        :param docker_build_directory:
        :return:
        """

        response = requests.get("https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json")
        dict_data = response.json()
        # Determine platform based on architecture
        if self.aws_lambda_api.configuration.architecture == "x86_64":
            platform = "linux64"
            docker_platform = "linux/amd64"
        else:
            platform = "linux-arm64"
            docker_platform = "linux/arm64"
        
        # Store docker platform for build process
        self.aws_lambda_api.build_api.configuration.docker_build_arguments = {
            "platform": docker_platform
        }
        downloads_dir = self.environment_api.configuration.data_directory_path / dict_data["channels"]["Stable"]["version"] / platform
        # /opt/hfrs/146.0.7680.31/linux64
        downloads_dir.mkdir(exist_ok=True, parents=True)
        chrome_directory = downloads_dir / "chrome"
        if not chrome_directory.exists():
            for chrome_dict in dict_data["channels"]["Stable"]["downloads"]["chrome"]:
                if chrome_dict["platform"] == platform:
                    download_chrome_url = chrome_dict["url"]
                    self.download_file(download_chrome_url, chrome_directory)
                    break

        chromedriver_directory = downloads_dir / "chromedriver"
        if not chromedriver_directory.exists():
            for chrome_dict in dict_data["channels"]["Stable"]["downloads"]["chromedriver"]:
                if chrome_dict["platform"] == platform:
                    download_chromedriver_url = chrome_dict["url"]
                    self.download_file(download_chromedriver_url, chromedriver_directory)
                    break

        shutil.copytree(chrome_directory, docker_build_directory/ "chrome")
        shutil.copytree(chromedriver_directory, docker_build_directory/"chromedriver")


        shutil.copy(self.configuration.horey_directory_path / "free_stuff_api" / "build" / "lambda_handler.py",
                    docker_build_directory)
        shutil.copy(self.configuration.horey_directory_path / "free_stuff_api" / "build" / "Dockerfile" , docker_build_directory)
        self.configuration.generate_configuration_file_ng(docker_build_directory/ "frs_api_configuration.json")

        return docker_build_directory

    @staticmethod
    def download_file(url: str, dst_dir_path: Path):
        """
        Download a file from a URL and save it locally.

        :param url:
        :param dst_dir_path:
        :return:
        """

        tmp_dir_path = dst_dir_path.parent / "tmp"

        file_name = url.split("/")[-1]
        logger.info(f"Downloading: {url} to {tmp_dir_path}")
        tmp_dir_path.mkdir(exist_ok=True, parents=True)
        file_path = tmp_dir_path / file_name
        # Use 'with' to ensure the connection is closed automatically
        with requests.get(url, stream=True) as r:
            r.raise_for_status()  # Check for HTTP errors (404, 500, etc.)
            with open(file_path, 'wb') as f:
                # Iterate in chunks of 8KB
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # Filter out keep-alive new chunks
                        f.write(chunk)

        # Open the ZIP file in read mode ('r') and extract all contents
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir_path)
            file_path.unlink()
        dirs = list(tmp_dir_path.iterdir())
        if len(dirs) != 1:
            raise NotImplementedError(dirs)
        dirs[0].move(dst_dir_path)
        shutil.rmtree(tmp_dir_path)

    def main(self):
        """
        Run the cycle.

        :return:
        """

        for platform in self.platforms:
            try:
                free_items = platform.api.get_free_items()
            except Exception as inst:
                logger.exception(inst)
                file_path = platform.api.selenium_api.get_screenshot()
                self.send_telegram_screenshot(file_path)
                raise

            for free_item in free_items:
                if self.add_free_item_to_db(platform, free_item):
                    self.notify_about_new_item(free_item)

        return True

    def provision_infra(self):
        """
        Provision infra.

        :return:
        """

        #self.db_api.provision_dynamo_table(self.configuration.dynamo_table_name)
        return self.aws_lambda_api.provision_docker_lambda()

    def update(self):
        """
        Provision code.

        :return:
        """

        return self.aws_lambda_api.update_docker_lambda()

    def trigger(self):
        """
        Trigger lambda

        :return:
        """

        res = self.aws_lambda_api.trigger_lambda()
        logger.info(f"Triggered lambda {res=}")

        self.aws_lambda_api.print_recent_execution_logs()
        return True

    def dispose_infra(self):
        # self.db_api.dispose_dynamo_table(self.configuration.dynamo_table_name)
        self.aws_lambda_api.dispose_docker_lambda()

    def add_free_item_to_db(self, platform, free_item: FreeItem):
        """
        Update or insert free item.

        :param platform:
        :param free_item:
        :return:
        """
        if free_item.url in platform.free_items:
            logger.info(f"Skipping already known item: {free_item.url}")
            return False
        breakpoint()
        format_string = "%Y-%m-%d %H:%M:%S.%f"

        sql_insert = """
            INSERT INTO tbl_free_items 
            (platform_id, name, description, url, image_url, address, ingestion_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """

        with sqlite3.connect(self.configuration.db_file_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")

            base_tuple = free_item.generate_db_tuple()
            data_tuple = (platform.id,) + base_tuple + (str(datetime.datetime.now(tz=datetime.timezone.utc).timestamp()),)
            breakpoint()
            try:
                cursor.execute(sql_insert, data_tuple)
                conn.commit()
            except Exception as inst_err:
                logger.exception(f"Error Inserting {repr(inst_err)}")
                if "UNIQUE constraint" in repr(inst_err):
                    logger.error(f"Data is not unique: {data_tuple}")
                    select_sql = "select * from auction_events where name=? or url=?"
                    ret = cursor.execute(select_sql, (auction_event.name, auction_event.url,))
                    lines = ret.fetchall()
                    self.delete_auction_event_with_lots(lines[0][0], connection=conn, cursor=cursor)
                    cursor.execute(sql_insert, data_tuple)
                    conn.commit()
                else:
                    logger.error(f"Unknown error with data: {data_tuple}")

                    #delete_sql = "DELETE from auction_events where url = ?"
                    #ret = cursor.execute(delete_sql, (lot.url,))
                    #logger.exception(f"Deleted: {ret.fetchall()}")
                    #cursor.execute(insert_sql, data_tuple)

                    # url = 'https://www.jardineauctioneers.com/auctions/24895-45th-annual-fredericton-sports-investment-auction?filter=(auction_ring_id:1200)'
                    # self.update_auction_event(23, url=url)
                    raise

        return True

    def provision_db_platforms_table(self):
        """
        Create table

        :return:
        """

        with sqlite3.connect(self.configuration.db_file_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tbl_platforms(
                    id INTEGER PRIMARY KEY ,
                    name TEXT NOT NULL UNIQUE
                )
            ''')
            conn.commit()  # Commit changes to the database
        logger.info(f"Database '{self.configuration.db_file_path}' created successfully with 'tbl_platforms' table.")


    def provision_db_free_items_table(self):
        """
        Create table

        :return:
        """

        with sqlite3.connect(self.configuration.db_file_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tbl_free_items(
                    id INTEGER PRIMARY KEY ,
                    platform_id INTEGER REFERENCES tbl_platforms(id) NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    image_url TEXT NOT NULL UNIQUE,
                    address TEXT NOT NULL,
                    ingestion_time TEXT,
                )
            ''')
            conn.commit()  # Commit changes to the database
        logger.info(f"Database '{self.configuration.db_file_path}' created successfully with 'tbl_free_items' table.")


    def provision_db(self):
        """
        Create tables
        :return:
        """

        self.provision_db_platforms_table()
        self.provision_db_free_items_table()
        return True

    def add_platform(self, platform: Platform):
        """
        Create table

        :return:
        """
        insert_sql = """
                    INSERT OR IGNORE INTO tbl_platforms 
                    (name)
                    VALUES (?)
                    """

        with sqlite3.connect(self.configuration.db_file_path) as conn:
            cursor = conn.cursor()
            cursor.execute(insert_sql, [platform.name])
            conn.commit()
        logger.info(f"Database '{self.configuration.db_file_path}' added {platform.name} to 'platform' table.")
        return True


    def notify_about_new_item(self, free_item: FreeItem):
        """
        Sends a message to a Telegram chat using a bot.

        Args:
            bot_token (str): The API token of your Telegram bot.
            chat_id (str or int): The chat ID of the recipient (user or group).
            message (str): The text of the message to send.

        Returns:
            bool: True if the message was sent successfully, False otherwise.
            :param free_item:
        """

        api_url = f"https://api.telegram.org/bot{self.configuration.telegram_bot_token}/sendMessage"
        params = {
            "chat_id": self.configuration.telegram_chat_id,
            "text": free_item.generate_message(),
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(api_url, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes
            return True
        except requests.exceptions.RequestException as e:
            logger.exception(e)
            return False

    def send_telegram_screenshot(self, img_path):
        """
             Sends a message to a Telegram chat using a bot.

             Args:
                 bot_token (str): The API token of your Telegram bot.
                 chat_id (str or int): The chat ID of the recipient (user or group).
                 message (str): The text of the message to send.

             Returns:
                 bool: True if the message was sent successfully, False otherwise.
                 :param free_item:
             """

        logger.info(f"Sending screenshot: {img_path}")

        api_url = f"https://api.telegram.org/bot{self.configuration.telegram_bot_token}/sendPhoto"

        with open(img_path, 'rb') as photo_file:
            files = {"photo": photo_file}

            params = {
            "chat_id": self.configuration.telegram_chat_id,
            "caption": "Screenshot from automation'"
            }
            try:
                response = requests.post(api_url, params=params, files=files)
                response.raise_for_status()  # Raise an exception for bad status codes
                return True
            except requests.exceptions.RequestException as e:
                logger.exception(e)
                return False
