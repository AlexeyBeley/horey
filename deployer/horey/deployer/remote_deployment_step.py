"""
Deployment step data class

"""

from horey.deployer.deployment_step import DeploymentStep

class RemoteDeploymentStep:
    """
    Single server deployment step
    """

    def __init__(self, name, enty_point):
        self.name = name
        self.enty_point = enty_point
        self.status = None
        self.status_code = None
        self.output = None

