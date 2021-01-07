"""
AWS rds client to handle rds service API requests.
"""
from boto3_client import Boto3Client
from rds_db_instance import DBInstance


class RDSClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """
    def __init__(self):
        client_name = "rds"
        super().__init__(client_name)

    def get_all_databases(self, full_information=True):
        """
        Get all databases
        :param full_information:
        :return:
        """
        final_result = list()

        for response in self.execute(self.client.describe_db_instances, "DBInstances"):

            obj = DBInstance(response)
            final_result.append(obj)

            if full_information:
                pass
        return final_result
