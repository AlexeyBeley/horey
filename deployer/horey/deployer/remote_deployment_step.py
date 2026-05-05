"""
Deployment step data class

"""


class RemoteDeploymentStep:
    """
    Single server deployment step
    """

    def __init__(self, name, entry_point, sleep_time=5, retry_attempts=12):
        self.name = name
        self.entry_point = entry_point
        self.sleep_time = sleep_time
        self.retry_attempts = retry_attempts
        self.status = None
        self.status_code = None
        self.output = None
