"""
AWS SESIdentity representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject

# pylint: disable= too-many-instance-attributes
class SESIdentity(AwsObject):
    """
    AWS SESIdentity class
    """

    def __init__(self, dict_src, from_cache=False):
        self.dkim_enabled = None
        self.dkim_verification_status = None
        self.dkim_signing_attributes = None
        self.dkim_attributes = None
        self.dkim_tokens = None
        self.behavior_on_mx_failure = None
        self.forwarding_enabled = None
        self.headers_in_bounce_notifications_enabled = None
        self.headers_in_complaint_notifications_enabled = None
        self.headers_in_delivery_notifications_enabled = None
        self.policies = None
        self.verification_status = None
        self.verification_token = None
        self.tags = None
        self.identity_type = None
        self.verified_for_sending_status = None
        self.configuration_set_name = None
        self.mail_from_attributes = None
        self.feedback_forwarding_status = None
        self.bounce_topic = None
        self.complaint_topic = None
        self.delivery_topic = None

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
            "IdentityName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
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
            "IdentityType": self.init_default_attr,
            "FeedbackForwardingStatus": self.init_default_attr,
            "VerifiedForSendingStatus": self.init_default_attr,
            "DkimAttributes": self.init_default_attr,
            "MailFromAttributes": self.init_default_attr,
            "Tags": self.init_default_attr,
            "SendingEnabled": self.init_default_attr,
            "VerificationInfo": self.init_default_attr,
            "BounceTopic": self.init_default_attr,
            "ComplaintTopic": self.init_default_attr,
            "DeliveryTopic": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard.

        :return:
        """

        request = {"EmailIdentity": self.name}
        self.extend_request_with_required_parameters(request, ["Tags"])
        self.extend_request_with_optional_parameters(request, ["DkimSigningAttributes", "ConfigurationSetName"])

        return request

    def generate_put_email_identity_configuration_set_attributes_request(self, desired_identity):
        """
        Standard

        :param desired_identity:
        :return:
        """

        if self.configuration_set_name != desired_identity.configuration_set_name:
            if desired_identity.configuration_set_name is not None:
                return {"EmailIdentity": self.name,
                        "ConfigurationSetName": desired_identity.configuration_set_name}
            raise NotImplementedError(
                    f"Only setting new configuration set is supported: {self.configuration_set_name=}, {desired_identity.configuration_set_name=}")
        return None

    def generate_set_identity_notification_topic_requests(self, desired_identity):
        """
        Standard.

        :param desired_identity: 
        :return: 
        """

        ret = []
        types = ["Bounce", "Complaint", "Delivery"]
        for notification_type in types:
            attr_name = f"{notification_type.lower()}_topic"
            if getattr(self, attr_name) != getattr(desired_identity, attr_name):
                request = {"Identity": self.name,
                           "NotificationType": notification_type,
                           "SnsTopic": getattr(desired_identity, attr_name)
                           }
                ret.append(request)
        return ret

    def generate_set_identity_headers_in_notifications_enabled_requests(self, desired_identity):
        """
        Standard.

        :param desired_identity: 
        :return: 
        """

        ret = []
        types = ["Bounce", "Complaint", "Delivery"]
        for notification_type in types:
            attr_name = f"headers_in_{notification_type.lower()}_notifications_enabled"
            if getattr(self, attr_name) != getattr(desired_identity, attr_name):
                request = {"Identity": self.name,
                           "NotificationType": notification_type,
                           "Enabled": getattr(desired_identity, attr_name)
                           }
                ret.append(request)
        return ret
