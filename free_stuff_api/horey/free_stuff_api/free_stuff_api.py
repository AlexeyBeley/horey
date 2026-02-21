from pathlib import Path

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

logger = get_logger()

class FreeStuffAPI:
    def __init__(self, configuration: FreeStuffAPIConfigurationPolicy = None):
        self.configuration = configuration
        self.platform_apis = [FacebookAPI()]
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
            self._aws_lambda_api = AWSLambdaAPI(configuration, self.environment_api)

            self._aws_lambda_api.build_api.prepare_docker_image_build_directory = lambda x, y: self._aws_lambda_api.build_api.prepare_docker_image_horey_package_build_directory(x, "free_stuff_api", y)

        return self._aws_lambda_api


    def main(self):
        """
        Run the cycle.

        :return:
        """

        for platform_api in self.platform_apis:
            free_items = platform_api.get_free_items()
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
        self.aws_lambda_api.provision_docker_lambda()

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