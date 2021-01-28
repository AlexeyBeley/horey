class Configuration:
    def __init__(self):
        self.jenkins_host = "jenkins.horey.com"
        self.jenkins_port = "443"
        self.jenkins_protocol = "https"
        self.jenkins_username = "horey_user"
        self.jenkins_token = "manually_generated_token"
        self.jenkins_timeout = 10


def main():
    configs = Configuration()
    return configs

