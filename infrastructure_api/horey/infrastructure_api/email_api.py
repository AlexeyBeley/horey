"""
Emails maintainer.

"""
from horey.h_logger import get_logger
from horey.aws_api.aws_services_entities.sesv2_configuration_set import SESV2ConfigurationSet
from horey.aws_api.aws_services_entities.ses_identity import SESIdentity
from horey.aws_api.aws_services_entities.sesv2_email_template import SESV2EmailTemplate

logger = get_logger()


class EmailAPI:
    """
    Manage Frontend.

    """

    def __init__(self, configuration, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api

    def provision(self):
        """
        Provision frontend.

        :return:
        """

        ret_identity = self.provision_ses_email_identity()
        ret_config_set = self.provision_ses_configuration_set()
        if not ret_identity and not ret_config_set:
            raise RuntimeError("Empty provision")
        return True

    def provision_ses_email_identity(self):
        """
        Provision and validate the identity to send emails from.

        :return:
        """

        if self.configuration.email_identity_name is None or self.configuration.email_identity_hosted_zone_name is None:
            return False

        return self.environment_api.provision_ses_domain_email_identity(name=self.configuration.email_identity_name,
                                                                        hosted_zone_name=self.configuration.email_identity_hosted_zone_name,
                                                                        configuration_set_name=self.configuration.email_identity_configuration_set)

    def provision_ses_configuration_set(self):
        """
        Provision config set.

        :return:
        """

        if self.configuration.configuration_set_name is None:
            return False

        configuration_set = SESV2ConfigurationSet({})
        configuration_set.name = self.configuration.configuration_set_name
        configuration_set.region = self.environment_api.region
        configuration_set.tracking_options = self.configuration.configuration_set_tracking_options
        configuration_set.reputation_options = {
                                                                          "ReputationMetricsEnabled": self.configuration.configuration_set_reputation_metrics_enabled
                                                                      }
        configuration_set.sending_options = {
                                                                          "SendingEnabled": self.configuration.configuration_set_sending_enabled
                                                                      }
        if self.configuration.configuration_set_event_destinations is not None:
            configuration_set.event_destinations = self.configuration.configuration_set_event_destinations
        configuration_set.tags = self.environment_api.configuration.tags
        configuration_set.tags.append({
            "Key": "Name",
            "Value": configuration_set.name
        })
        return self.environment_api.aws_api.sesv2_client.provision_configuration_set(configuration_set, declerative=True)

    def send_email(self, dst_address):
        """
        Send test email from identity.

        :param dst_address:
        :return:
        """

        from_address = f"horey@{self.configuration.email_identity_name}"
        dict_request = {"FromEmailAddress": from_address,
                        "Destination": {"ToAddresses": [dst_address, ]},
                        "Content": {'Simple': {"Subject": {
                            "Data": "Hello"},
                            "Body": {
                                "Text": {
                                    "Data": "world",
                                }}
                        }},
                        "EmailTags": [
                            {
                                "Name": "Name",
                                "Value": "Horey"
                            },
                        ],
                        }
        response = self.environment_api.aws_api.sesv2_client.send_email_raw(self.environment_api.region, request_dict=dict_request)
        logger.info(f"Sent email to {dst_address}, message_id: {response}")
        return response

    def get_template(self, template_name):
        """
        Standard.

        :param template_name:
        :return:
        """
        template = SESV2EmailTemplate({})
        template.name = template_name
        template.region = self.environment_api.region

        if not self.environment_api.aws_api.sesv2_client.update_email_template_information(template):
            return None

        return template

    def get_identity(self, identity_name):
        """
        Standard.

        :param identity_name:
        :return:
        """

        identity = SESIdentity({})
        identity.name = identity_name
        identity.region = self.environment_api.region
        if not self.environment_api.aws_api.sesv2_client.update_identity_information(identity):
            return None
        return identity

    def get_configuration_set(self, configuration_set_name):
        """
        Standard.

        :param configuration_set_name:
        :return:
        """

        for region_config_set in self.environment_api.aws_api.sesv2_client.yield_configuration_sets(region=self.environment_api.region):
            if region_config_set.name == configuration_set_name:
                return region_config_set

        return None

    def get_suppressed_emails(self):
        """
        Get suppressed destinations.

        :return:
        """

        return self.environment_api.aws_api.sesv2_client.get_region_suppressed_destinations(self.environment_api.region)

    def unsupress_email(self, src_email):
        """
        Delete the email from suppression list.

        :param src_email:
        :return:
        """

        return self.environment_api.aws_api.sesv2_client.delete_suppressed_destination_raw(self.environment_api.region, {"EmailAddress": src_email})
