"""
AWS SESV2ConfigurationSet representation
"""
import copy

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class SESV2ConfigurationSet(AwsObject):
    """
    AWS SESV2ConfigurationSet class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.tags = None
        self.event_destinations = []
        self.tracking_options = None
        self.reputation_options = None
        self.sending_options = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "ConfigurationSetName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "TrackingOptions": self.init_default_attr,
            "ReputationOptions": self.init_default_attr,
            "SendingOptions": self.init_default_attr,
            "Tags": self.init_default_attr,
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
        Update self attributes from raw AWS API response.

        :param dict_src:
        :return:
        """

        init_options = {
            "ConfigurationSetName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "TrackingOptions": self.init_default_attr,
            "ReputationOptions": self.init_default_attr,
            "SendingOptions": self.init_default_attr,
            "Tags": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Create conf set request.

        :return:
        """

        request = {"ConfigurationSetName": self.name, "Tags": self.tags, "TrackingOptions": self.tracking_options,
                   "ReputationOptions": self.reputation_options, "SendingOptions": self.sending_options}
        return request

    def generate_create_requests_event_destinations(self):
        """
        Generate requests to add event_destinations.

        :return:
        """

        lst_ret = []
        for event_destination_tmp in self.event_destinations:
            event_destination = copy.deepcopy(event_destination_tmp)
            del event_destination["Name"]
            dict_request = {"ConfigurationSetName": self.name,
                            "EventDestinationName": event_destination_tmp["Name"],
                            "EventDestination": event_destination}
            lst_ret.append(dict_request)

        return lst_ret

    @property
    def region(self):
        if self._region is not None:
            return self._region

        raise NotImplementedError("region")

    @region.setter
    def region(self, value):
        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value
