"""
Authorization Job

"""

from horey.h_logger import get_logger
from horey.jenkins_manager.authorization_job.authorization_applicator import AuthorizationApplicator

logger = get_logger()


class AuthorizationJob:
    """
    Main class.

    """

    def __init__(self, configuration):
        self.configuration = configuration
        self.authorization_applicator = AuthorizationApplicator()
        self.authorization_applicator.deserialize(configuration.authorization_map_file_path)

    def authorize(self, request):
        """
        Authorize user.

        @return:
        """
        return self.authorization_applicator.authorize(request)
