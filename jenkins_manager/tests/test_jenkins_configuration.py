"""
Running tests of several jenkins_manager possibilities.
Not really tests but more like a usage demonstration.
"""
import os
import sys


sys.path.insert(0, os.path.abspath("../horey/jenkins_manager"))


from jenkins_configuration import JenkinsConfiguration


def test_init_from_python_file():
    """
    Run the cleanup function and save the output to file.
    :return:
    """
    config = JenkinsConfiguration()
    config.init_from_dictionary(
        {
            "configuration_file_full_path": os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "jenkins_configuration_file.py",
            )
        }
    )
    config.init_from_file()
    assert config.jenkins_host == "test_host"
    assert config.jenkins_port == "443"
    # self.jenkins_host = "test_host"
    # self.jenkins_port = "443"
    # self.jenkins_protocol = "https"
    # self.jenkins_username = "test_username"
    # self.jenkins_token = "test_token"
    # self.jenkins_timeout = 10


test_init_from_python_file()
