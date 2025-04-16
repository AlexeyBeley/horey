"""
AWS lambda client to handle lambda service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.aws_services_entities.backups_recovery_point import BackupsRecoveryPoint

from horey.h_logger import get_logger

logger = get_logger()


class BackupClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    Validate fingerprint
    openssl pkcs8 -in file_name.pem -inform PEM -outform DER -topk8 -nocrypt | openssl sha1 -c
    """

    def __init__(self):
        client_name = "backup"
        super().__init__(client_name)

    def yield_recovery_points(self, region=None, update_info=False):
        """
        Yield recovery_points

        :return:
        """

        regional_fetcher_generator = self.yield_recovery_points_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                                    BackupsRecoveryPoint,
                                                                    update_info=update_info,
                                                                    regions=[region] if region else None)
    
    def yield_recovery_points_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        if filters_req is not None and filters_req.get("BackupVaultName") is not None:
            vaults = [filters_req.get("BackupVaultName")]
        else:
            vaults = [response["BackupVaultName"] for response in self.execute(
                self.get_session_client(region=region).list_backup_vaults, "BackupVaultList",
                filters_req=filters_req)]

        for vault_name in vaults:
            vault_filter = {"BackupVaultName": vault_name}
            yield from self.execute(
                    self.get_session_client(region=region).list_recovery_points_by_backup_vault, "RecoveryPoints",
                    filters_req=vault_filter
            )

        return None

    def get_all_recovery_points(self, region=None, update_info=False):
        """
        Get all acm_recovery_points in all regions.

        :return:
        """

        return list(self.yield_recovery_points(region=region, update_info=update_info))
    
    def delete_recovery_point_raw(self, region, filters_req):
        """
        response = client.delete_recovery_point(
        BackupVaultName='string',
        RecoveryPointArn='string'
        )

        :return:
        """

        logger.info(f"Disposing recovery point: {filters_req}")
        for response in self.execute(
                    self.get_session_client(region=region).delete_recovery_point, None, raw_data=True, filters_req=filters_req):

            return response
