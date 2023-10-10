"""
Base Boto3 client. It provides sessions and client management.
"""

import os
import datetime
import json
import time
from horey.aws_api.aws_clients.sessions_manager import SessionsManager
from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.common_utils.common_utils import CommonUtils

logger = get_logger()


class Boto3Client:
    """
    Main class to inherite from, when creating AWS clients.
    """

    EXEC_COUNT = 0
    SESSIONS_MANAGER = SessionsManager()
    EXECUTION_RETRY_COUNT = 1000
    NEXT_PAGE_REQUEST_KEY = "NextToken"
    NEXT_PAGE_RESPONSE_KEY = "NextToken"
    NEXT_PAGE_INITIAL_KEY = None
    DEBUG = False
    _main_cache_dir_path = None

    def __init__(self, client_name):
        """
        self.client shouldn't be inited, the init should be done on demand if execute is called
        Client is a singleton identified by client_name and region_name

        :param client_name:

        """

        self.client_name = client_name
        self._account_id = None

    @property
    def main_cache_dir_path(self):
        """
        The highest level cache dir path

        :return:
        """

        if Boto3Client._main_cache_dir_path is None:
            raise ValueError("Main cache dir was not set in boto3_client.py")
        return Boto3Client._main_cache_dir_path

    @main_cache_dir_path.setter
    def main_cache_dir_path(self, value):
        if not os.path.exists(value):
            raise ValueError(f"Not existing cache dir: {value}")
        if not os.path.isdir(value):
            raise ValueError(f"main_cache_dir_path must point to a dir: {value}")
        Boto3Client._main_cache_dir_path = value

    @property
    def client_cache_dir_name(self):
        """
        This client's dir name.

        :return:
        """

        return CommonUtils.camel_case_to_snake_case(self.__class__.__name__)

    @property
    def account_id(self):
        """
        AWS account id - str

        :return:
        """

        if self._account_id is None:
            sts_client = self.SESSIONS_MANAGER.get_client("sts")
            self._account_id = sts_client.get_caller_identity()["Account"]
        return self._account_id

    @property
    def client(self):
        """
        Returns current sessions AWS client, which executes the base api calls
        :return:
        """
        return self.SESSIONS_MANAGER.get_client(self.client_name)

    @client.setter
    def client(self, _):
        """
        As the clients are managed by session manager they can't be assigned explicitly.
        :param _:
        :return:
        """
        raise RuntimeError(f"Nobody can set a client explicitly in{self}")

    # pylint: disable= too-many-arguments
    def yield_with_paginator(
        self,
        func_command,
        return_string,
        filters_req=None,
        raw_data=False,
        internal_starting_token=False,
        exception_ignore_callback=None,
    ):
        """
        Function to yeild replies, if there is no need to get all replies.
        It can save API requests if the expected information found before.

        :param func_command: Bound method from _client instance
        :param return_string: string to retrive the infromation from reply dict
        :param filters_req: filters dict passed to the API client to filter the response
        :param exception_ignore_callback: called on exception if returns true - do not retries on exception
        :return: list of replies
        """

        if filters_req is None:
            filters_req = {}

        starting_token = self.NEXT_PAGE_INITIAL_KEY
        retry_counter = 0
        while retry_counter < self.EXECUTION_RETRY_COUNT:
            try:
                logger.info(
                    f"Start paginating with starting_token: '{starting_token}'"
                )
                if self.DEBUG:
                    logger.info(
                        f"Start paginating with starting_token: '{starting_token}' and args '{filters_req}'"
                    )

                for result, new_starting_token in self.unpack_pagination_loop(
                    starting_token,
                    func_command.__name__,
                    return_string,
                    filters_req,
                    raw_data=raw_data,
                    internal_starting_token=internal_starting_token,
                ):
                    retry_counter = 0
                    starting_token = new_starting_token
                    yield result
                break
            except self.NoReturnStringError:
                raise
            except Exception as exception_instance:
                logger.warning(
                    f"Exception received in paginator '{func_command.__name__}' Error: {repr(exception_instance)}"
                )
                if "The security token included in the request is invalid" in repr(
                    exception_instance
                ):
                    raise
                exception_weight = 10
                time_to_sleep = 1

                if "Throttling" in repr(exception_instance):
                    exception_weight = 1
                    time_to_sleep = retry_counter + exception_weight
                    logger.error(
                        f"Retrying after Throttling '{func_command.__name__}' attempt {retry_counter}/{self.EXECUTION_RETRY_COUNT} Error: {exception_instance}"
                    )

                if exception_ignore_callback is not None and exception_ignore_callback(
                    exception_instance
                ):
                    return

                if  "AccessDenied" in repr(exception_instance):
                    raise

                if "UnauthorizedOperation" in repr(exception_instance):
                    raise

                retry_counter += exception_weight
                time.sleep(time_to_sleep)
                logger.warning(
                    f"Retrying '{func_command.__name__}' attempt {retry_counter}/{self.EXECUTION_RETRY_COUNT} Error: {exception_instance}"
                )
        else:
            raise TimeoutError(
                f"Max attempts reached while executing '{func_command.__name__}': {self.EXECUTION_RETRY_COUNT}"
            )

    # pylint: disable= too-many-arguments
    def unpack_pagination_loop(
        self,
        starting_token,
        func_command_name,
        return_string,
        filters_req,
        raw_data=False,
        internal_starting_token=False,
    ):
        """
        Fetch data from single pagination loop run.

        :param starting_token:
        :param func_command_name:
        :param return_string:
        :param filters_req:
        :param raw_data:
        :param internal_starting_token:
        :return:
        """
        for _page in self.client.get_paginator(func_command_name).paginate(
            PaginationConfig={self.NEXT_PAGE_REQUEST_KEY: starting_token}, **filters_req
        ):

            starting_token = self.unpack_pagination_loop_starting_token(
                _page, return_string, internal_starting_token
            )
            logger.info(
                f"Updating '{func_command_name}' {filters_req} pagination starting_token: {starting_token}"
            )

            Boto3Client.EXEC_COUNT += 1

            if raw_data:
                yield _page, starting_token
            else:
                if return_string not in _page:
                    raise self.NoReturnStringError(
                        f"Has no return string '{return_string}'. Return dict: {_page}"
                    )
                if isinstance(_page[return_string], list):
                    for response_obj in _page[return_string]:
                        yield response_obj, starting_token
                elif isinstance(_page[return_string], dict):
                    yield _page[return_string], starting_token
                else:
                    raise NotImplementedError(
                        f"Unexpected return type: {type(_page[return_string])}"
                    )

            if starting_token is None:
                return

    def unpack_pagination_loop_starting_token(
        self, _page, return_string, internal_starting_token
    ):
        """
        Fetch starting token from internal data.

        :param _page:
        :param return_string:
        :param internal_starting_token:
        :return:
        """

        if internal_starting_token:
            return _page.get(return_string).get(self.NEXT_PAGE_RESPONSE_KEY)

        return _page.get(self.NEXT_PAGE_RESPONSE_KEY)

    # pylint: disable= too-many-arguments
    def execute_old(
        self,
        func_command,
        return_string,
        filters_req=None,
        raw_data=False,
        internal_starting_token=False,
        exception_ignore_callback=None,
    ):
        """
        Command to execute clients bound function- execute with paginator if available.

        :param func_command: Bound method from _client instance
        :param return_string: string to retrive the infromation from reply dict
        :param filters_req: filters dict passed to the API client to filter the response
        :param exception_ignore_callback: called on exception if returns true - do not retries on exception
        :return: list of replies
        """

        if filters_req is None:
            filters_req = {}

        if self.client.can_paginate(func_command.__name__):
            for ret_obj in self.yield_with_paginator(
                func_command,
                return_string,
                filters_req=filters_req,
                raw_data=raw_data,
                internal_starting_token=internal_starting_token,
                exception_ignore_callback=exception_ignore_callback,
            ):
                yield ret_obj
            return

        Boto3Client.EXEC_COUNT += 1
        try:
            response = func_command(**filters_req)
        except Exception as exception_instance:
            logger.warning(
                f"Exception received '{func_command.__name__}' Error: {repr(exception_instance)}"
            )
            if exception_ignore_callback is not None and exception_ignore_callback(
                exception_instance
            ):
                return
            raise

        if raw_data:
            yield response
            return

        if isinstance(response[return_string], list):
            ret_lst = response[return_string]
        elif type(response[return_string]) in [str, dict, type(None), bool]:
            ret_lst = [response[return_string]]
        else:
            raise NotImplementedError(f"{response[return_string]} type:{type(response[return_string])}")

        for ret_obj in ret_lst:
            yield ret_obj
    # pylint: disable= too-many-arguments

    def execute(
        self,
        func_command,
        return_string,
        filters_req=None,
        raw_data=False,
        internal_starting_token=False,
        exception_ignore_callback=None,
        instant_raise=False,
    ):
        """
        Command to execute clients bound function- execute with paginator if available.

        :param instant_raise: Raise without protection
        :param func_command: Bound method from _client instance
        :param return_string: string to retrive the infromation from reply dict
        :param filters_req: filters dict passed to the API client to filter the response
        :param exception_ignore_callback: called on exception if returns true - do not retries on exception
        :return: list of replies
        """

        if filters_req is None:
            filters_req = {}

        if self.client.can_paginate(func_command.__name__):
            for ret_obj in self.yield_with_paginator(
                func_command,
                return_string,
                filters_req=filters_req,
                raw_data=raw_data,
                internal_starting_token=internal_starting_token,
                exception_ignore_callback=exception_ignore_callback,
            ):
                yield ret_obj
            return

        response = self.execute_without_pagination(func_command, return_string, filters_req=filters_req, raw_data=raw_data, exception_ignore_callback=exception_ignore_callback, instant_raise=instant_raise)

        for ret_obj in response:
            yield ret_obj

    # pylint: disable= too-many-branches
    def execute_without_pagination(self, func_command, return_string, filters_req=None, raw_data=False, exception_ignore_callback=None, instant_raise=False):
        """
        Protected execution of an API call.

        :param instant_raise:
        :param return_string:
        :param func_command:
        :param filters_req:
        :param exception_ignore_callback:
        :return:
        """

        retry_counter = 0
        while retry_counter < self.EXECUTION_RETRY_COUNT:
            Boto3Client.EXEC_COUNT += 1
            try:
                logger.info(
                    f"Executing: '{func_command.__name__}'"
                )
                if self.DEBUG:
                    logger.info(
                        f"Executing: '{func_command.__name__}' and args '{filters_req}'"
                    )
                response = func_command(**filters_req)
                break
            except Exception as exception_instance:
                logger.warning(
                    f"Exception received in paginator '{func_command.__name__}' Error: {repr(exception_instance)}"
                )
                if "The security token included in the request is invalid" in repr(
                    exception_instance
                ):
                    raise
                exception_weight = 10
                time_to_sleep = 1

                if "Throttling" in repr(exception_instance):
                    exception_weight = 1
                    time_to_sleep = retry_counter + exception_weight
                    logger.error(
                        f"Retrying after Throttling '{func_command.__name__}' attempt {retry_counter}/{self.EXECUTION_RETRY_COUNT} Error: {exception_instance}"
                    )

                if exception_ignore_callback is not None and exception_ignore_callback(
                    exception_instance
                ):
                    return []

                if "AccessDenied" in repr(exception_instance):
                    raise

                if "UnauthorizedOperation" in repr(exception_instance):
                    raise

                if "UnauthorizedOperation" in repr(exception_instance):
                    raise

                if "AuthFailure" in repr(exception_instance):
                    raise

                if instant_raise:
                    raise

                retry_counter += exception_weight
                time.sleep(time_to_sleep)
                logger.warning(
                    f"Retrying '{func_command.__name__}' attempt {retry_counter}/{self.EXECUTION_RETRY_COUNT} Error: {exception_instance}"
                )
        else:
            raise TimeoutError(
                    f"Max attempts reached while executing '{func_command.__name__}': {self.EXECUTION_RETRY_COUNT}"
                )

        if raw_data:
            ret_value = response
        else:
            ret_value = response[return_string]

        if isinstance(ret_value, list):
            return ret_value

        if type(ret_value) in [str, dict, type(None), bool]:
            return [ret_value]

        raise NotImplementedError(f"{ret_value} type:{type(ret_value)}")

    # pylint: disable= too-many-arguments
    def execute_with_single_reply(
            self,
            func_command,
        return_string,
        filters_req=None,
        raw_data=False,
        internal_starting_token=False,
        exception_ignore_callback=None,
    ):
        """
        Wait for a single result.

        @param func_command:
        @param return_string:
        @param filters_req:
        @param raw_data:
        @param internal_starting_token:
        @param exception_ignore_callback:
        @return:
        """

        ret = list(
            self.execute(
                func_command,
                return_string,
                filters_req=filters_req,
                raw_data=raw_data,
                internal_starting_token=internal_starting_token,
                exception_ignore_callback=exception_ignore_callback,
            )
        )
        if len(ret) == 1:
            return ret[0]

        if len(ret) == 0:
            raise self.ZeroValuesException(str(ret))

        raise self.ToManyValuesException(str(ret))

    # pylint: disable= too-many-arguments
    @staticmethod
    def wait_for_status(
        observed_object,
        update_function,
        desired_statuses,
        permit_statues,
        error_statuses,
        timeout=300,
        sleep_time=5,
    ):
        """
        Wait for status change


        @param observed_object: AWS object to be observed. MUST have 'get_status' method.
        @param update_function: Callback used to update the status.
        @param desired_statuses: Statuses we want to achieve- break the loop. (Success, Available etc.)
        @param permit_statues: Statuses we permit to be as intermediate status. (Waiting, InProgress etc.)
        @param error_statuses: Statuses indicating failure. (Failed, Error etc.)
        @param timeout:
        @param sleep_time:
        @return:
        """
        start_time = datetime.datetime.now()
        logger.info(
            f"Starting waiting loop for {observed_object.id} to become one of {desired_statuses}"
        )

        for i in range(timeout // sleep_time):
            update_function(observed_object)

            try:
                object_status = observed_object.get_status()
            except observed_object.UndefinedStatusError:
                time.sleep(sleep_time)
                continue

            if object_status in desired_statuses:
                break

            if object_status in error_statuses:
                raise RuntimeError(
                    f"{observed_object.id} is in error status: {object_status}"
                )

            if permit_statues and object_status not in permit_statues:
                raise RuntimeError(
                    f"Permit statuses were set but {observed_object.id} is in a different status: {object_status}"
                )

            logger.info(
                f"[{i * sleep_time}/{timeout} seconds] Status waiter for {observed_object.id} is going to sleep for {sleep_time}. Status: {object_status}"
            )
            time.sleep(sleep_time)
        else:
            raise TimeoutError(
                f"Did not reach one of the desired status {desired_statuses} for {timeout} seconds. Current status: {object_status}"
            )

        end_time = datetime.datetime.now()
        logger.info(
            f"Finished waiting loop for {observed_object.id} to become one of {desired_statuses}. Took {end_time - start_time}"
        )

    def get_tags(self, obj, function=None, arn_identifier="ResourceArn", tags_identifier="Tags"):
        """
        Get tags for resource.

        :param obj:
        :param function:
        :param arn_identifier:
        :param tags_identifier:
        :return:
        """

        if function is None:
            function = self.client.get_tags

        logger.info(f"Getting resource tags: {obj.arn}")
        ret = list(
            self.execute(function, tags_identifier, filters_req={arn_identifier: obj.arn})
        )
        obj.tags = ret
        return ret

    def tag_resource(self, obj, arn_identifier="ResourceArn", tags_identifier="TagsToAdd"):
        """
        Tag resource.

        :param obj:
        :param arn_identifier:
        :param tags_identifier:
        :return:
        """

        logger.info(f"Tagging resource: {obj.arn}")
        for response in self.execute(
            self.client.tag_resource,
            "Tags",
            filters_req={arn_identifier: obj.arn, tags_identifier: obj.tags},
            raw_data=True,
        ):
            return response

    class NoReturnStringError(Exception):
        """
        No such return string in response.

        """

    class ResourceNotFoundError(ValueError):
        """
        No such resource.

        """

    class ZeroValuesException(RuntimeError):
        """
        No values.

        """

    class ToManyValuesException(RuntimeError):
        """
        To many values.

        """

    @staticmethod
    def cache_objects(objects, file_path, indent=4):
        """
        Cache the objects.

        :param objects:
        :param file_path:
        :param indent:
        :return:
        """
        if objects is None:
            return

        objects_dicts = [obj.convert_to_dict() for obj in objects]

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file_handler:
            json.dump(objects_dicts, file_handler, indent=indent)

    def clear_cache(self, entity_class):
        """
        Clear all cache of this entity class

        :param entity_class:
        :return:
        """

        aws_api_account = AWSAccount.get_aws_account()
        cache_dir = os.path.join(self.main_cache_dir_path, aws_api_account.name)
        if not os.path.exists(cache_dir):
            return False
        entity_class_file_raw_name = entity_class.get_cache_file_name().replace(".json", "")

        logger.info(f"Starting clearing cache per region in '{cache_dir}'")
        for region_name in os.listdir(cache_dir):
            logger.info(f"Starting clearing regional cache for '{region_name}'")
            region_client_dir = os.path.join(cache_dir, region_name, self.client_cache_dir_name)
            if not os.path.exists(region_client_dir):
                continue
            logger.info(f"Starting clearing regional cache for client dir '{self.client_cache_dir_name}'")
            for file_name in os.listdir(region_client_dir):
                if entity_class_file_raw_name in file_name:
                    cache_file_path = os.path.join(region_client_dir, file_name)
                    logger.info(f"Clearing cache at '{cache_file_path}'")
                    os.remove(cache_file_path)
        return True

    def add_entity_to_cache(self, entity, full_information, get_tags):
        """
        Add new entity.

        :param get_tags:
        :param full_information:
        :param entity:
        :return:
        """

        file_path = self.generate_cache_file_path(entity.__class__, entity.region.region_mark, full_information, get_tags)
        if os.path.exists(file_path):
            with open(file_path, encoding="utf-8") as file_handler:
                objects = json.load(file_handler)

            objects.append(entity.convert_to_dict())
            with open(file_path, "w", encoding="utf-8") as file_handler:
                json.dump(objects, file_handler, indent=4)

    def generate_cache_file_path(self, class_type, region_dir_name, full_information, get_tags):
        """
        Generate cache file path to write and read from.

        :param get_tags:
        :param full_information:
        :param class_type:
        :param region_dir_name:
        :return:
        """

        file_name = class_type.get_cache_file_name()
        if file_name.count(".") != 1:
            raise ValueError(f"Unsupported cache file name. Single dot should present: {file_name}")

        if full_information:
            file_name = file_name.replace(".", "_full_info.")
        if get_tags:
            file_name = file_name.replace(".", "_tags.")
        aws_api_account = AWSAccount.get_aws_account()
        return os.path.join(self.main_cache_dir_path, aws_api_account.name, region_dir_name, self.client_cache_dir_name, file_name)

    @staticmethod
    def load_objects_from_cache(class_type, file_path):
        """
        Load objects from cached file

        @param file_path:
        @param class_type:
        @return:
        """

        logger.info(f"Loading '{class_type}' objects from cache file: {file_path}")

        if not os.path.exists(file_path):
            return None
        with open(file_path, encoding="utf-8") as file_handler:
            return [
                class_type(dict_src, from_cache=True) for dict_src in json.load(file_handler)
            ]

    def regional_service_entities_generator(self, regional_fetcher_generator,
                                      entity_class,
                                      full_information_callback=None,
                                      get_tags_callback=None,
                                      update_info=False,
                                      regions=None,
                                      global_service=False,
                                      filters_req=None):
        """
        Be sure you know what you do, when you set full_information=True.
        This can kill your memory, if you have a lot of data.
        For example in Cloudwatch or S3.
        Sometimes it's better using yield* or explicitly setting full_information=None

        :param filters_req: Request input params if any.
        :param regional_fetcher_generator: The lowest API facing function. Retrieves raw dictionaries.
        :param entity_class: Class of the entity to init with the raw Data.
        :param full_information_callback: Get excessive information
        :param get_tags_callback: Fetch tags separately from the main data request
        :param update_info: Fetch the data form AWS API
        :param regions: regions to fetch the entities from
        :param global_service: no need to go over all regions - use the one set in AWSAccount or the first one of available
        :return:
        """

        if global_service:
            if regions:
                raise ValueError(f"Can not set both {global_service=} and {regions=}")
            region = AWSAccount.get_aws_region()
            if region is None:
                regions = list(AWSAccount.get_aws_account().regions.values())[:1]
            else:
                regions = [region]

        if not isinstance(update_info, bool):
            raise ValueError(f"update_info must be bool, received: '{update_info}'")

        if not regions:
            regions = AWSAccount.get_aws_account().regions.values()

        if not regions:
            raise ValueError(f"Was not able to find region while fetching {entity_class} information.")

        for region in regions:
            for obj in  self.region_service_entities_generator(
                region, regional_fetcher_generator, entity_class,
                full_information_callback=full_information_callback,
                get_tags_callback=get_tags_callback,
                update_info=update_info,
                filters_req=filters_req
            ):
                yield obj

    def region_service_entities_generator(self, region,
                                          regional_fetcher_generator,
                                          entity_class,
                                          full_information_callback=None,
                                          get_tags_callback=None,
                                          update_info=False,
                                          filters_req=None):
        """
        Get region log groups.

        :param regional_fetcher_generator:
        :param entity_class:
        :param full_information_callback:
        :param get_tags_callback:
        :param update_info:
        :param filters_req:
        :param region:
        :return:
        """

        full_information = full_information_callback is not None
        get_tags = get_tags_callback is not None
        file_name = self.generate_cache_file_path(entity_class, region.region_mark, full_information, get_tags)
        if not update_info and not filters_req:
            objects = self.load_objects_from_cache(entity_class, file_name)
            if objects is not None:
                for obj in objects:
                    yield obj
                return

        final_result = []
        AWSAccount.set_aws_region(region)
        for result in regional_fetcher_generator(filters_req=filters_req):
            obj = entity_class(result)
            if full_information_callback:
                full_information_callback(obj)
            if get_tags_callback:
                get_tags_callback(obj)
            obj.region = region
            final_result.append(obj)
            yield obj
        if filters_req is None:
            self.cache_objects(final_result, file_name)
