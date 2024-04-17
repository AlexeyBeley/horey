"""
Manages sessions towards multiple AWS accounts and regions.
"""
import threading
import datetime
import time
from typing import Any
import boto3
import botocore
from dateutil.tz import tzlocal
from horey.h_logger import get_logger

from horey.aws_api.base_entities.aws_account import AWSAccount

logger = get_logger()


class LockAcquiringFailError(Exception):
    """
    Exception acquiring lock.
    """


class SessionsManager:
    """
    Class to handle multiple sessions to different accounts.
    """

    CONNECTIONS = {}  # {Session: {client_name: client}}
    ASSUME_ROLE_SESSION_EXPIRY_WINDOW_SECONDS = 60 * 15

    class Connection:
        """
        Class to handle a connection on the same AWS API session to multiple clients.
        """

        LOCK = threading.Lock()

        def __init__(self, session):
            self.session = session
            self.clients = {}

        def get_client(self, client_name, region):
            """
            If client to a specific region does not exist, create it.

            :param region:
            :param client_name:
            :return:
            """
            region_mark = region.region_mark
            if (
                    region_mark not in self.clients
                    or client_name not in self.clients[region_mark]
            ):
                self.connect_client(region_mark, client_name)

            return self.clients[region_mark][client_name]

        def connect_client(self, region_mark, client_name):
            """
            Create a client connection in specific region
            :param region_mark:
            :param client_name:
            :return:
            """
            # pylint: disable= consider-using-with
            try:
                for _ in range(10):
                    acquired = SessionsManager.Connection.LOCK.acquire(blocking=False)
                    if acquired is True:
                        if region_mark not in self.clients:
                            self.clients[region_mark] = {}

                        if client_name in self.clients[region_mark]:
                            return

                        self.clients[region_mark][client_name] = self.session.client(
                            client_name, region_name=region_mark
                        )
                        break
                    time.sleep(1)
                else:
                    raise LockAcquiringFailError()
            finally:
                SessionsManager.Connection.LOCK.release()

    @staticmethod
    def get_connection_id(region=None):
        """
        Each connection has a unique id- in order to reuse it. This function generates it.
        :return:
        """
        aws_account = AWSAccount.get_aws_account()
        aws_account_id = "default_account" if aws_account is None else aws_account.id

        aws_region = region or AWSAccount.get_aws_region()
        region_mark = aws_region.region_mark if aws_region is not None else ""
        return f"{aws_account_id}/{region_mark}"

    @staticmethod
    def get_connection(region=None):
        """
        AWS connection to an account.
        :return: Connects Session if there is no one already
        """

        connection_id = SessionsManager.get_connection_id(region=region)
        connection = SessionsManager.CONNECTIONS.get(connection_id)
        if connection is not None:
            return connection

        session = SessionsManager.connect_session(region=region)
        connection = SessionsManager.Connection(session)
        SessionsManager.add_new_connection(connection_id, connection)

        return connection

    @staticmethod
    def execute_connection_step(connection_step, session, region=None):
        """
        Executes on of AWS accounts' connection the steps.

        :param region:
        :param connection_step:
        :param session:
        :return:
        """
        current_used_region = region or AWSAccount.get_aws_region()
        if current_used_region is None:
            region_name = connection_step.region.region_mark if connection_step.region is not None else None
        else:
            region_name = current_used_region.region_mark

        if connection_step.external_id is not None:
            extra_args = {"ExternalId": connection_step.external_id}
        else:
            extra_args = None

        if connection_step.type == connection_step.Type.PROFILE:
            logger.info(f"Connecting session using profile: {connection_step.profile_name}")
            if session is not None:
                raise RuntimeError("Initial session is not None")

            session = boto3.session.Session(
                profile_name=connection_step.profile_name,
                region_name=region_name,
            )
        elif connection_step.type == connection_step.Type.ASSUME_ROLE:
            logger.info("Connecting session using assumed role")
            session = SessionsManager.start_assuming_role(
                connection_step.role_arn, session, extra_args=extra_args
            )
        elif connection_step.type == connection_step.Type.CURRENT_ROLE:
            logger.info("Connecting session using current role")
            session = boto3.session.Session(
                region_name=region_name
            )
        elif connection_step.type == connection_step.Type.CREDENTIALS:
            logger.info(f"Connecting session using credentials. Region: '{region_name}'")
            session = boto3.session.Session(
                aws_access_key_id=connection_step.aws_access_key_id,
                aws_secret_access_key=connection_step.aws_secret_access_key,
                region_name=region_name
            )
        else:
            raise NotImplementedError(
                f"Unknown connection_step type: {connection_step.type}"
            )

        return session

    @staticmethod
    def connect_session(region=None):
        """
        Each account can be managed after several steps of connection - run all steps in order to connect.
        :return:
        """
        session = None
        aws_account = AWSAccount.get_aws_account()

        if aws_account is None or len(aws_account.connection_steps) == 0:
            session = boto3.session.Session()
        else:
            for connection_step in aws_account.connection_steps:
                session = SessionsManager.execute_connection_step(
                    connection_step, session, region=region
                )

        if session is None:
            raise RuntimeError(
                f"Could not establish session for aws_account {aws_account.id}"
            )
        return session

    @staticmethod
    def add_new_connection(aws_account, connection):
        """
        Add connection to specific AWS account.

        :param aws_account:
        :param connection:
        :return:
        """
        SessionsManager.CONNECTIONS[aws_account] = connection

    @staticmethod
    def start_assuming_role(role_arn: str, session: Any, extra_args=None):
        """
        Automatically refreshes sessions
        Shamelessly stolen from here:
        https://stackoverflow.com/questions/45518122/boto3-sts-assumerole-with-mfa-working-example

        :param extra_args: Any additional arguments to add to the assume
            role request using the format of the botocore operation.
            Possible keys include, but may not be limited to,
            DurationSeconds, Policy, SerialNumber, ExternalId and
            RoleSessionName.
        :param session:
        :param role_arn:
        :return: session
        """

        fetcher = botocore.credentials.AssumeRoleCredentialFetcher(
            client_creator=session._session.create_client,
            source_credentials=session.get_credentials(),
            role_arn=role_arn,
            expiry_window_seconds=SessionsManager.ASSUME_ROLE_SESSION_EXPIRY_WINDOW_SECONDS,
            extra_args=extra_args,
        )

        creds = botocore.credentials.DeferredRefreshableCredentials(
            method="assume-role",
            refresh_using=fetcher.fetch_credentials,
            time_fetcher=lambda: datetime.datetime.now(tzlocal()),
        )
        botocore_session = botocore.session.Session()
        botocore_session._credentials = creds

        return boto3.Session(botocore_session=botocore_session)

    @staticmethod
    def get_client(client_name, region=None):
        """
        Connects if no clients

        :param region:
        :param client_name:
        :return:
        """

        connection = SessionsManager.get_connection(region=region)
        return connection.get_client(client_name, region)
