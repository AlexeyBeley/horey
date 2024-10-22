"""
Jenkins API configuration policy
"""
import copy

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

#pylint: disable= missing-function-docstring


class JenkinsAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class.

    """
    def __init__(self):
        super().__init__()
        self._host = None
        self._username = None
        self._token = None
        self._timeout = None
        self._cache_dir_path = None
        self._region = "us-west-2"
        self._vpc_name = "vpc_jenkins"
        self._vpc_primary_subnet = "192.168.0.0/24"
        self._hagent_security_group_name = "sg_jenkins_hagent"
        self._tags = [{
            "Key": "Owner",
            "Value": "Horey"
        }]
        self._hagent_cluster_name = "jenkins_hagent_cluster"
        self._iam_path = "/jenkins/"
        self._hagent_container_instance_role_name = "role_jenkins_hagent_container_instance"
        self._hagent_container_instance_profile_name = "instance_profile_jenkins_hagent_container_instance"

    @property
    def hagent_container_instance_profile_name(self):
        return self._hagent_container_instance_profile_name

    @hagent_container_instance_profile_name.setter
    def hagent_container_instance_profile_name(self, value):
        self._hagent_container_instance_profile_name = value
        
    @property
    def hagent_container_instance_role_name(self):
        return self._hagent_container_instance_role_name

    @hagent_container_instance_role_name.setter
    def hagent_container_instance_role_name(self, value):
        self._hagent_container_instance_role_name = value

    @property
    def iam_path(self):
        return self._iam_path

    @iam_path.setter
    def iam_path(self, value):
        self._iam_path = value

    @property
    def hagent_cluster_name(self):
        return self._hagent_cluster_name

    @hagent_cluster_name.setter
    def hagent_cluster_name(self, value):
        self._hagent_cluster_name = value

    @property
    def tags(self):
        return copy.deepcopy(self._tags)

    @tags.setter
    def tags(self, value):
        self._tags = value

    @property
    def hagent_security_group_name(self):
        return self._hagent_security_group_name

    @hagent_security_group_name.setter
    def hagent_security_group_name(self, value):
        self._hagent_security_group_name = value

    @property
    def vpc_primary_subnet(self):
        return self._vpc_primary_subnet

    @vpc_primary_subnet.setter
    def vpc_primary_subnet(self, value):
        self._vpc_primary_subnet = value

    @property
    def vpc_name(self):
        return self._vpc_name

    @vpc_name.setter
    def vpc_name(self, value):
        self._vpc_name = value

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, value):
        self._region = value

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self._timeout = value

    @property
    def cache_dir_path(self):
        return self._cache_dir_path

    @cache_dir_path.setter
    def cache_dir_path(self, value):
        self._cache_dir_path = value
