"""
AWS AutoScalingActivity representation
"""

from enum import Enum
from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.common_utils.common_utils import CommonUtils


class AutoScalingActivity(AwsObject):
    """
    AWS AutoScalingActivity class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.status_code = None


        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "ActivityId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            )
        }

        self.init_attrs(dict_src, init_options)

    def _init_object_from_cache(self, dict_src):
        """
        Init from cache
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def update_from_raw_response(self, dict_src):
        """
        Response from server.

        @param dict_src:
        @return:
        """
        init_options = {
            "ActivityId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
        }
        self.init_attrs(dict_src, init_options)

    def get_status(self):
        """
        For the status_waiter.

        :return:
        """

        breakpoint()
        if self.status_code is None:
            raise self.UndefinedStatusError()
        return {
            enum_value.value: enum_value
            for _, enum_value in self.Status.__members__.items()
        }[CommonUtils.camel_case_to_snake_case(self.status_code).upper()]

    class Status(Enum):
        """
            from horey.common_utils.common_utils import CommonUtils
            ret = ['PendingSpotBidPlacement' , 'WaitingForSpotInstanceRequestId' , 'WaitingForSpotInstanceId' ,
            'WaitingForInstanceId' , 'PreInService' , 'InProgress' , 'WaitingForELBConnectionDraining' ,
            'MidLifecycleAction' , 'WaitingForInstanceWarmup' , 'Successful' , 'Failed' ,
            'Cancelled' , 'WaitingForConnectionDraining']

            for i, x in enumerate(ret): print(CommonUtils.camel_case_to_snake_case(x).upper() + " = " + str(i))

        """

        PENDING_SPOT_BID_PLACEMENT = 0
        WAITING_FOR_SPOT_INSTANCE_REQUEST_ID = 1
        WAITING_FOR_SPOT_INSTANCE_ID = 2
        WAITING_FOR_INSTANCE_ID = 3
        PRE_IN_SERVICE = 4
        IN_PROGRESS = 5
        WAITING_FOR_ELB_CONNECTION_DRAINING = 6
        MID_LIFECYCLE_ACTION = 7
        WAITING_FOR_INSTANCE_WARMUP = 8
        SUCCESSFUL = 9
        FAILED = 10
        CANCELLED = 11
        WAITING_FOR_CONNECTION_DRAINING = 12
