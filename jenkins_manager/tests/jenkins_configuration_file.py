class Configuration:
    def __init__(self):
        self.jenkins_host = "test_host"
        self.jenkins_port = "443"
        self.jenkins_protocol = "https"
        self.jenkins_username = "test_username"
        self.jenkins_token = "test_token"
        self.jenkins_timeout = 10


def main():
    configs = Configuration()
    return configs

