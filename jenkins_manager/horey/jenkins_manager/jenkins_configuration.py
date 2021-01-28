from horey.configuration.configuration import Configuration


class JenkinsConfiguration(Configuration):
    def __init__(self):
        super().__init__()
        self._jenkins_host = None
        self._jenkins_username = None
        self._jenkins_token = None
        self._jenkins_protocol = None
        self._jenkins_port = None
        self._jenkins_timeout = None

    @property
    def jenkins_host(self):
        return self._jenkins_host

    @jenkins_host.setter
    def jenkins_host(self, value):
        self._jenkins_host = value

    @property
    def jenkins_username(self):
        return self._jenkins_username

    @jenkins_username.setter
    def jenkins_username(self, value):
        self._jenkins_username = value

    @property
    def jenkins_token(self):
        return self._jenkins_token

    @jenkins_token.setter
    def jenkins_token(self, value):
        self._jenkins_token = value

    @property
    def jenkins_protocol(self):
        return self._jenkins_protocol

    @jenkins_protocol.setter
    def jenkins_protocol(self, value):
        self._jenkins_protocol = value

    @property
    def jenkins_port(self):
        return self._jenkins_port

    @jenkins_port.setter
    def jenkins_port(self, value):
        self._jenkins_port = value

    @property
    def jenkins_timeout(self):
        return self._jenkins_timeout

    @jenkins_timeout.setter
    def jenkins_timeout(self, value):
        self._jenkins_timeout = value
