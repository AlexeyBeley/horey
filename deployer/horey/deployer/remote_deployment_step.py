"""
Deployment step data class

"""


class RemoteDeploymentStep:
    """
    Single server deployment step
    """

    def __init__(self, name, entry_point):
        self.name = name
        self.entry_point = entry_point
        self.sleep_time = 5
        self.retry_attempts = 12
        self.status = None
        self.status_code = None
        self.output = None
