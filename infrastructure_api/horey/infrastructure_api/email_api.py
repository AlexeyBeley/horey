"""
Emails maintainer.

"""


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

        return self.environment_api.provision_sesv2_configuration_set(name=self.configuration.configuration_set_name,
                                                                      configuration_set_tracking_options=self.configuration.configuration_set_tracking_options,
                                                                      reputation_options={
                                                                          "ReputationMetricsEnabled": self.configuration.configuration_set_reputation_metrics_enabled
                                                                      },
                                                                      sending_options={
                                                                          "SendingEnabled": self.configuration.configuration_set_sending_enabled
                                                                      },
                                                                      event_destinations=self.configuration.configuration_set_event_destinations)
