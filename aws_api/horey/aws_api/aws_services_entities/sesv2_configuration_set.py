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

        request = {"ConfigurationSetName": self.name, "Tags": self.tags,
                   "ReputationOptions": self.reputation_options, "SendingOptions": self.sending_options}

        self.extend_request_with_optional_parameters(request, ["TrackingOptions"])
        return request

    def generate_event_destinations_requests(self, desired_configuration_set):
        """
        Generate requests to add event_destinations.

        :return:
        """
        create_requests, update_requests, delete_requests = [], [], []
        current_event_destinations_to_names = {event_destination["Name"]: event_destination for event_destination in self.event_destinations}
        desired_event_destinations_to_names = {event_destination["Name"]: event_destination for event_destination in desired_configuration_set.event_destinations}
        for desired_event_destination_name, desired_event_destination in desired_event_destinations_to_names.items():
            if desired_event_destination_name not in current_event_destinations_to_names:
                event_destination = copy.deepcopy(desired_event_destination)
                del event_destination["Name"]
                dict_request = {"ConfigurationSetName": self.name,
                                "EventDestinationName": desired_event_destination_name,
                                "EventDestination": event_destination}
                create_requests.append(dict_request)
            elif desired_event_destination != current_event_destinations_to_names[desired_event_destination_name]:
                event_destination = copy.deepcopy(desired_event_destination)
                del event_destination["Name"]
                dict_request = {"ConfigurationSetName": self.name,
                                "EventDestinationName": desired_event_destination_name,
                                "EventDestination": event_destination}
                update_requests.append(dict_request)

        for current_event_destination_name in current_event_destinations_to_names:
            if current_event_destination_name not in current_event_destinations_to_names:
                dict_request = {"ConfigurationSetName": self.name,
                                "EventDestinationName": current_event_destination_name,
                              }
                delete_requests.append(dict_request)

        return create_requests, update_requests, delete_requests

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

    @property
    def arn(self):
        """
        Standard.

        :return:
        """
        return f"arn:aws:ses:{self.region.region_mark}:{self.account_id}:configuration-set/{self.name}"
