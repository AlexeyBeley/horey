"""
AWS SESIdentity representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class SESIdentity(AwsObject):
    """
    AWS SESIdentity class
    """

    def __init__(self, dict_src, from_cache=False):
        self.dkim_enabled = None
        self.dkim_verification_status = None
        self.dkim_tokens = None
        self.behavior_on_mx_failure = None
        self.forwarding_enabled = None
        self.headers_in_bounce_notifications_enabled = None
        self.headers_in_complaint_notifications_enabled = None
        self.headers_in_delivery_notifications_enabled = None
        self.policies = None
        self.verification_status = None
        self.verification_token = None

        super().__init__(dict_src)

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        self.update_from_raw_response(dict_src)

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
        dict received from server.

        for key_name in dict_src: print(f"self.{self.format_attr_name(key_name)} = None")

        :param dict_src:
        :return:
        """

        init_options = {
            "name": self.init_default_attr,
            "DkimEnabled": self.init_default_attr,
            "DkimVerificationStatus": self.init_default_attr,
            "DkimTokens": self.init_default_attr,
            "BehaviorOnMXFailure": self.init_default_attr,
            "ForwardingEnabled": self.init_default_attr,
            "HeadersInBounceNotificationsEnabled": self.init_default_attr,
            "HeadersInComplaintNotificationsEnabled": self.init_default_attr,
            "HeadersInDeliveryNotificationsEnabled": self.init_default_attr,
            "Policies": self.init_default_attr,
            "VerificationStatus": self.init_default_attr,
            "VerificationToken": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)
