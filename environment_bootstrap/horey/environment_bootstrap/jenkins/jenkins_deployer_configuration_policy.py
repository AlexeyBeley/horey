from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class JenkinsDeployerConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._jenkins_ec2_instance_type = None
        self._aws_api_configuration_values_file_path = None
        self._jenkins_manager_configuration_values_file_path = None

    @property
    def jenkins_ec2_instance_type(self):
        return self._jenkins_ec2_instance_type

    @jenkins_ec2_instance_type.setter
    def jenkins_ec2_instance_type(self, value):
        self._jenkins_ec2_instance_type = value

    @property
    def aws_api_configuration_values_file_path(self):
        return self._aws_api_configuration_values_file_path

    @aws_api_configuration_values_file_path.setter
    def aws_api_configuration_values_file_path(self, value):
        self._aws_api_configuration_values_file_path = value

    @property
    def jenkins_manager_configuration_values_file_path(self):
        return self._jenkins_manager_configuration_values_file_path

    @jenkins_manager_configuration_values_file_path.setter
    def jenkins_manager_configuration_values_file_path(self, value):
        self._jenkins_manager_configuration_values_file_path = value
