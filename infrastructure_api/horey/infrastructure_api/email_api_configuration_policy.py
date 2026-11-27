"""
AWS ECS config

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-instance-attributes


class EmailAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._email_identity_name = None
        self._email_identity_hosted_zone_name = None
        self._configuration_set_name = None
        self._configuration_set_tracking_options = None
        self._configuration_set_reputation_metrics_enabled = None
        self._configuration_set_sending_enabled = None
        self._email_identity_configuration_set = None
        self._configuration_set_event_destinations = None

    @property
    def configuration_set_event_destinations(self):
        return self._configuration_set_event_destinations

    @configuration_set_event_destinations.setter
    def configuration_set_event_destinations(self, value):
        self._configuration_set_event_destinations = value

    @property
    def email_identity_configuration_set(self):
        if self._email_identity_configuration_set is None:
            raise self.UndefinedValueError("email_identity_configuration_set")
        return self._email_identity_configuration_set

    @email_identity_configuration_set.setter
    def email_identity_configuration_set(self, value):
        self._email_identity_configuration_set = value

    @property
    def configuration_set_sending_enabled(self):
        if self._configuration_set_sending_enabled is None:
            raise self.UndefinedValueError("configuration_set_sending_enabled")
        return self._configuration_set_sending_enabled

    @configuration_set_sending_enabled.setter
    def configuration_set_sending_enabled(self, value):
        self._configuration_set_sending_enabled = value

    @property
    def configuration_set_reputation_metrics_enabled(self):
        if self._configuration_set_reputation_metrics_enabled is None:
            raise self.UndefinedValueError("configuration_set_reputation_metrics_enabled")
        return self._configuration_set_reputation_metrics_enabled

    @configuration_set_reputation_metrics_enabled.setter
    def configuration_set_reputation_metrics_enabled(self, value):
        self._configuration_set_reputation_metrics_enabled = value

    @property
    def configuration_set_tracking_options(self):
        return self._configuration_set_tracking_options

    @configuration_set_tracking_options.setter
    def configuration_set_tracking_options(self, value):
        self._configuration_set_tracking_options = value

    @property
    def configuration_set_name(self):
        return self._configuration_set_name

    @configuration_set_name.setter
    def configuration_set_name(self, value):
        self._configuration_set_name = value

    @property
    def email_identity_hosted_zone_name(self):
        return self._email_identity_hosted_zone_name

    @email_identity_hosted_zone_name.setter
    def email_identity_hosted_zone_name(self, value):
        self._email_identity_hosted_zone_name = value

    @property
    def email_identity_name(self):
        return self._email_identity_name

    @email_identity_name.setter
    def email_identity_name(self, value):
        self._email_identity_name = value
