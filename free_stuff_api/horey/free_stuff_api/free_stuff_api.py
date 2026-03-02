import shutil
import time
from datetime import datetime, timezone
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

logger = get_logger()

class FreeStuffAPI:
    def __init__(self, configuration: FreeStuffAPIConfigurationPolicy = None):
        self.configuration = configuration

        self.platform_apis = [FacebookAPI(selenium_api=SeleniumAPI(chromedriver_path=Path("/opt/chrome-driver/chromedriver"),
                                                                   chrome_path=Path("/opt/chrome/chrome")))]
        self._db_api = None
        self._environment_api = None
        self._aws_lambda_api = None

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

        for platform_api in self.platform_apis:
            try:
                free_items = platform_api.get_free_items()
            except Exception as inst:
                logger.exception(inst)
                file_path = platform_api.selenium_api.get_screenshot()
                self.send_telegram_screenshot(file_path)
                raise

            for free_item in free_items:
                if self.add_free_item_to_db(free_item):
                    self.notify_about_new_item(free_item)

                # todo: remove break
                break

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
        breakpoint()
        return True

    def dispose_infra(self):
        # self.db_api.dispose_dynamo_table(self.configuration.dynamo_table_name)
        self.aws_lambda_api.dispose_docker_lambda()

    def add_free_item_to_db(self, free_item: FreeItem):
        """
        Add item to db. Return true if new.

        :param free_item:
        :return:
        """

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
