"""
AWS rds client to handle rds service API requests.
"""
# pylint: disable= too-many-lines
import datetime
import time
from collections import defaultdict

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.rds_db_instance import RDSDBInstance
from horey.aws_api.aws_services_entities.rds_db_cluster import RDSDBCluster
from horey.aws_api.aws_services_entities.rds_db_subnet_group import RDSDBSubnetGroup
from horey.aws_api.aws_services_entities.rds_db_cluster_parameter_group import (
    RDSDBClusterParameterGroup,
)
from horey.aws_api.aws_services_entities.rds_db_cluster_snapshot import (
    RDSDBClusterSnapshot,
)
from horey.aws_api.aws_services_entities.rds_db_parameter_group import (
    RDSDBParameterGroup,
)
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.h_logger import get_logger

logger = get_logger()


class RDSClient(Boto3Client):
    """
    Main class.

    """

    NEXT_PAGE_REQUEST_KEY = "Marker"
    NEXT_PAGE_RESPONSE_KEY = "Marker"
    ENGINE_VERSIONS = defaultdict(dict)
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "rds"
        super().__init__(client_name)

    # pylint: disable= too-many-arguments
    def yield_db_instances(self, region=None, update_info=False, filters_req=None, get_tags=True):
        """
        Yield db_instances

        :return:
        """

        regional_fetcher_generator = self.yield_db_instances_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            RDSDBInstance,
                                                            update_info=update_info,
                                                            get_tags_callback=self.get_tags if get_tags else None,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_db_instances_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
            self.get_session_client(region=region).describe_db_instances, "DBInstances", filters_req=filters_req
        )

    def get_all_db_instances(self, region=None):
        """
        Get all db_instances in all regions.
        :return:
        """

        return list(self.yield_db_instances(region=region))

    def get_region_db_instances(self, region, filters=None, update_tags=True):
        """
        Standard.

        :param region:
        :param filters:
        :param update_tags:
        :return:
        """

        return list(self.yield_db_instances(region=region, filters_req=filters, get_tags=update_tags))

    # pylint: disable= too-many-arguments
    def yield_db_clusters(self, region=None, update_info=False, full_information=True, filters_req=None, get_tags=True):
        """
        Yield db_clusters

        :return:
        """

        regional_fetcher_generator = self.yield_db_clusters_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            RDSDBCluster,
                                                            update_info=update_info,
                                                            full_information_callback=self.update_cluster_full_information if full_information else None,
                                                            get_tags_callback=self.get_tags if get_tags else None,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_db_clusters_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
            self.get_session_client(region=region).describe_db_clusters, "DBClusters", filters_req=filters_req
        )

    def get_all_db_clusters(self, region=None, full_information=False, filters_req=None, get_tags=None,
                            update_info=False):
        """
        Get all db_clusters in all regions.
        :return:
        """

        return list(self.yield_db_clusters(region=region, filters_req=filters_req, get_tags=get_tags,
                                           full_information=full_information, update_info=update_info))

    def get_region_db_clusters(self, region, filters=None, update_tags=True, full_information=False):
        """
        Standard.

        :param region:
        :param filters:
        :param update_tags:
        :param full_information:
        :return:
        """

        return list(self.yield_db_clusters(region=region, filters_req=filters, get_tags=update_tags,
                                           full_information=full_information))

    def update_cluster_full_information(self, cluster):
        """
        Fetch excessive information.

        :param cluster:
        :return:
        """

        cluster.default_engine_version = self.get_default_engine_version(cluster.region, cluster.engine)
        return cluster

    def provision_db_cluster(self, db_cluster: RDSDBCluster, snapshot_id=None, timeout=60*60):
        """
        Standard.

        :param timeout:
        :param db_cluster:
        :param snapshot_id:
        :return:
        """

        if snapshot_id is not None:
            return self.restore_db_cluster_from_snapshot(db_cluster, snapshot_id)

        region_db_clusters = self.get_region_db_clusters(db_cluster.region)
        for region_db_cluster in region_db_clusters:
            if db_cluster.id == region_db_cluster.id:
                return db_cluster.update_from_raw_response(region_db_cluster.dict_src)

        response = self.provision_db_cluster_raw(db_cluster.region, db_cluster.generate_create_request())
        db_cluster.update_from_raw_response(response)

        return self.wait_for_status(
            db_cluster,
            self.update_db_cluster_information,
            [db_cluster.Status.AVAILABLE],
            [db_cluster.Status.CREATING,
             db_cluster.Status.MODIFYING,
             db_cluster.Status.REBOOTING,
             db_cluster.Status.BACKING_UP,
             ],
            [db_cluster.Status.FAILED, db_cluster.Status.DELETING],
            timeout=timeout
        )

    def provision_db_cluster_raw(self, region, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Creating db_cluster: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_db_cluster, "DBCluster", filters_req=request_dict
        ):
            self.clear_cache(RDSDBCluster)
            return response

    def dispose_db_cluster(self, db_cluster: RDSDBCluster):
        """
        Standard.

        :param db_cluster:
        :return:
        """

        region_db_clusters = self.get_region_db_clusters(db_cluster.region)
        for region_db_cluster in region_db_clusters:
            if db_cluster.id == region_db_cluster.id:
                db_cluster.update_from_raw_response(region_db_cluster.dict_src)
                break
        else:
            return

        filters_req = {"Filters": [
            {
                "Name": "db-cluster-id",
                "Values": [
                    db_cluster.id,
                ],
            }
        ]}

        if "postgres" not in db_cluster.engine:
            db_instances = self.get_region_db_instances(
                region=db_cluster.region, filters=filters_req
            )
            for db_instance in db_instances:
                db_instance.region = db_cluster.region
                db_instance.skip_final_snapshot = db_cluster.skip_final_snapshot
                self.dispose_db_instance(db_instance)

        response = self.dispose_db_cluster_raw(db_cluster.region, db_cluster.generate_dispose_request())

        db_cluster.update_from_raw_response(response)

        try:
            self.wait_for_status(
                db_cluster,
                self.update_db_cluster_information,
                [],
                [db_cluster.Status.DELETING, db_cluster.Status.AVAILABLE],
                [],
                timeout=20 * 60,
            )
        except self.ResourceNotFoundError:
            pass

    def dispose_db_cluster_raw(self, region, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Disposing db_cluster: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).delete_db_cluster, "DBCluster", filters_req=request_dict
        ):
            self.clear_cache(RDSDBCluster)
            return response

    def dispose_db_instance(self, db_instance: RDSDBInstance):
        """
        Standard.

        :param db_instance:
        :return:
        """

        response = self.dispose_db_instance_raw(db_instance.region, db_instance.generate_dispose_request())
        if response is None:
            return True
        db_instance.update_from_raw_response(response)
        try:
            self.wait_for_status(
                db_instance,
                self.update_db_instance_information,
                [db_instance.Status.STOPPED],
                [db_instance.Status.DELETING],
                [db_instance.Status.FAILED,
                 db_instance.Status.AVAILABLE],
                timeout=20 * 60 * 60,
            )
        except self.ResourceNotFoundError:
            pass
        return True

    def dispose_db_instance_raw(self, region, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Disposing db_instance: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).delete_db_instance, "DBInstance", filters_req=request_dict,
                exception_ignore_callback=lambda error: "DBInstanceNotFound" in repr(error)
        ):
            self.clear_cache(RDSDBInstance)
            return response

    def restore_db_cluster_from_snapshot(self, db_cluster, snapshot_id):
        """
        Standard.

        :param db_cluster:
        :param snapshot_id:
        :return:
        """

        response = self.restore_db_cluster_from_snapshot_raw(db_cluster.region,
                                                             db_cluster.generate_restore_db_cluster_from_snapshot_request(
                                                                 snapshot_id)
                                                             )
        db_cluster.update_from_raw_response(response)
        return db_cluster

    def restore_db_cluster_from_snapshot_raw(self, region, request_dict):
        """
        Returns ARN
        """
        logger.info(f"restoring db_cluster from snapshot: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).restore_db_cluster_from_snapshot,
                "DBCluster",
                filters_req=request_dict,
        ):
            self.clear_cache(RDSDBCluster)
            return response

    # pylint: disable= too-many-arguments
    def yield_db_subnet_groups(self, region=None, update_info=False, filters_req=None):
        """
        Yield db_subnet_groups

        :return:
        """

        regional_fetcher_generator = self.yield_db_subnet_groups_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            RDSDBSubnetGroup,
                                                            update_info=update_info,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_db_subnet_groups_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
            self.get_session_client(region=region).describe_db_subnet_groups, "DBSubnetGroups",
            filters_req=filters_req
        )

    def get_all_db_subnet_groups(self, region=None):
        """
        Get all db_subnet_groups in all regions.
        :return:
        """

        return list(self.yield_db_subnet_groups(region=region))

    def get_region_db_subnet_groups(self, region):
        """
        Standard.

        :param region:
        :return:
        """

        return list(self.yield_db_subnet_groups(region=region))

    def provision_db_subnet_group(self, db_subnet_group: RDSDBSubnetGroup):
        """
        Standard.

        :param db_subnet_group:
        :return:
        """
        region_db_subnet_groups = self.get_region_db_subnet_groups(
            db_subnet_group.region
        )
        for region_db_subnet_group in region_db_subnet_groups:
            if db_subnet_group.name == region_db_subnet_group.name:

                request = region_db_subnet_group.generate_modify_request(db_subnet_group)
                if request:
                    update_info = self.modify_db_subnet_group_raw(db_subnet_group.region, request)
                else:
                    update_info = region_db_subnet_group.dict_src
                db_subnet_group.update_from_raw_response(update_info)

                return db_subnet_group

        response = self.provision_db_subnet_group_raw(db_subnet_group.region,
                                                      db_subnet_group.generate_create_request()
                                                      )
        db_subnet_group.update_from_raw_response(response)
        return db_subnet_group

    def dispose_db_subnet_group(self, db_subnet_group: RDSDBSubnetGroup):
        """
        Standard.

        :param db_subnet_group:
        :return:
        """
        region_db_subnet_groups = self.get_region_db_subnet_groups(
            db_subnet_group.region
        )
        for region_db_subnet_group in region_db_subnet_groups:
            if db_subnet_group.name == region_db_subnet_group.name:
                break
        else:
            return None

        self.delete_db_subnet_group_raw(db_subnet_group.region,
                                        {"DBSubnetGroupName": db_subnet_group.name}
                                        )
        return None

    def provision_db_subnet_group_raw(self, region, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Creating db_subnet_group: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_db_subnet_group,
                "DBSubnetGroup",
                filters_req=request_dict,
        ):
            self.clear_cache(RDSDBSubnetGroup)
            return response

    def modify_db_subnet_group_raw(self, region, request_dict):
        """
        Returns dict
        """
        logger.info(f"Modifying db_subnet_group: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).modify_db_subnet_group,
                "DBSubnetGroup",
                filters_req=request_dict,
        ):
            self.clear_cache(RDSDBSubnetGroup)
            return response

    def delete_db_subnet_group_raw(self, region, request_dict):
        """
        Returns dict
        """

        logger.info(f"Deleting db_subnet_group: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).delete_db_subnet_group,
                None,
                raw_data=True,
                filters_req=request_dict,
        ):
            self.clear_cache(RDSDBSubnetGroup)
            return response

    # pylint: disable= too-many-arguments
    def yield_db_cluster_parameter_groups(self, region=None, update_info=False, filters_req=None,
                                          full_information=True):
        """
        Yield db_cluster_parameter_groups

        :return:
        """
        full_information_callback = self.get_db_cluster_parameters_group_full_information if full_information else None
        regional_fetcher_generator = self.yield_db_cluster_parameter_groups_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            RDSDBClusterParameterGroup,
                                                            update_info=update_info,
                                                            full_information_callback=full_information_callback,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_db_cluster_parameter_groups_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
            self.get_session_client(region=region).describe_db_cluster_parameter_groups, "DBClusterParameterGroups",
            filters_req=filters_req
        )

    def get_all_db_cluster_parameter_groups(self, region=None):
        """
        Get all db_cluster_parameter_groups in all regions.
        :return:
        """

        return list(self.yield_db_cluster_parameter_groups(region=region))

    def get_region_db_cluster_parameter_groups(self, region, full_information=True):
        """
        Standard.

        :param region:
        :param full_information:
        :return:
        """

        return list(self.yield_db_cluster_parameter_groups(region=region, full_information=full_information))

    def get_db_cluster_parameters_group_full_information(self, obj):
        """
        Standard.

        :param obj:
        :return:
        """

        filters_req = {"DBClusterParameterGroupName": obj.name}
        obj.parameters = []
        for response_param in self.execute(
                self.get_session_client(region=obj.region).describe_db_cluster_parameters,
                "Parameters",
                filters_req=filters_req,
        ):
            obj.parameters.append(response_param)

        return obj

    # pylint: disable= too-many-arguments
    def yield_db_cluster_snapshots(self, region=None, update_info=False, full_information=True, filters_req=None,
                                   get_tags=True):
        """
        Yield db_cluster_snapshots

        :return:
        """

        full_information_callback = self.update_db_cluster_snapshot_full_information if full_information else None
        regional_fetcher_generator = self.yield_db_cluster_snapshots_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            RDSDBClusterSnapshot,
                                                            update_info=update_info,
                                                            get_tags_callback=self.get_tags if get_tags else None,
                                                            full_information_callback=full_information_callback,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_db_cluster_snapshots_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
            self.get_session_client(region=region).describe_db_cluster_snapshots,
            "DBClusterSnapshots",
            filters_req=filters_req,
            exception_ignore_callback=lambda x: "DBClusterSnapshotNotFoundFault"
                                                in repr(x),
        )

    def get_all_db_cluster_snapshots(self, region=None):
        """
        Get all db_cluster_snapshot in all regions.
        :return:
        """

        return list(self.yield_db_cluster_snapshots(region=region))

    def get_region_db_cluster_snapshots(
            self, region, full_information=True, custom_filters=None, update_tags=True
    ):
        """
        Standard.

        :param region:
        :param full_information:
        :param custom_filters:
        :param update_tags:
        :return:
        """

        return list(self.yield_db_cluster_snapshots(region=region, full_information=full_information,
                                                    filters_req=custom_filters, get_tags=update_tags))

    def update_db_cluster_snapshot_full_information(self, obj):
        """
        Standard.

        :param obj:
        :return:
        """
        filters_req = {"DBClusterSnapshotIdentifier": obj.id}
        obj.parameters = []
        for response_param in self.execute(
                self.get_session_client(region=obj.region).describe_db_cluster_snapshot_attributes,
                "DBClusterSnapshotAttributesResult",
                filters_req=filters_req,
        ):
            obj.parameters.append(response_param)
        return obj

    def get_all_db_parameter_groups(self, region=None):
        """
        Get all db_parameter_groups in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_db_parameter_groups(region)

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_db_parameter_groups(_region)

        return final_result

    def get_region_db_parameter_groups(self, region, full_information=True):
        """
        Standard.

        :param region:
        :param full_information:
        :return:
        """

        final_result = []
        for response in self.execute(
                self.get_session_client(region=region).describe_db_parameter_groups, "DBParameterGroups"
        ):
            obj = RDSDBParameterGroup(response)
            final_result.append(obj)
            if full_information:
                filters_req = {"DBParameterGroupName": obj.name}
                obj.parameters = []
                for response_param in self.execute(
                        self.get_session_client(region=region).describe_db_parameters,
                        "Parameters",
                        filters_req=filters_req,
                ):
                    obj.parameters.append(response_param)

        return final_result

    def provision_db_cluster_parameter_group(self, db_cluster_parameter_group):
        """
        Standard.

        :param db_cluster_parameter_group:
        :return:
        """

        region_db_cluster_parameter_groups = (
            self.get_region_db_cluster_parameter_groups(
                db_cluster_parameter_group.region
            )
        )

        for region_db_cluster_parameter_group in region_db_cluster_parameter_groups:
            if (
                    db_cluster_parameter_group.name
                    == region_db_cluster_parameter_group.name
            ):
                db_cluster_parameter_group.update_from_raw_response(
                    region_db_cluster_parameter_group.dict_src
                )
                return db_cluster_parameter_group

        response = self.provision_db_cluster_parameter_group_raw(db_cluster_parameter_group.region,
                                                                 db_cluster_parameter_group.generate_create_request()
                                                                 )
        db_cluster_parameter_group.update_from_raw_response(response)
        return db_cluster_parameter_group

    def provision_db_cluster_parameter_group_raw(self, region, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Creating db_cluster_parameter_group: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_db_cluster_parameter_group,
                "DBClusterParameterGroup",
                filters_req=request_dict,
        ):
            self.clear_cache(RDSDBClusterParameterGroup)
            return response

    def dispose_cluster_parameter_group(self, param_group):
        """
        Standard.

        :param param_group:
        :return:
        """

        request_dict = {"DBClusterParameterGroupName": param_group.name}
        logger.info(f"Disposing db_cluster_parameter_group: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=param_group.region).delete_db_cluster_parameter_group,
                None,
                raw_data=True,
                filters_req=request_dict,
                exception_ignore_callback=lambda error: "DBParameterGroupNotFound" in repr(error)
        ):
            self.clear_cache(RDSDBClusterParameterGroup)
            return response

    def dispose_parameter_group(self, param_group):
        """
        Standard.

        :param param_group:
        :return:
        """
        request_dict = {"DBParameterGroupName": param_group.name}
        logger.info(f"Disposing db_parameter_group: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=param_group.region).delete_db_parameter_group,
                None,
                raw_data=True,
                filters_req=request_dict,
                exception_ignore_callback=lambda error: "DBParameterGroupNotFound" in repr(error)
        ):
            self.clear_cache(RDSDBParameterGroup)
            return response

    def provision_db_parameter_group(self, db_parameter_group):
        """
        Standard.

        :param db_parameter_group:
        :return:
        """

        region_db_parameter_groups = self.get_region_db_parameter_groups(
            db_parameter_group.region
        )
        for region_db_parameter_group in region_db_parameter_groups:
            if db_parameter_group.name == region_db_parameter_group.name:
                db_parameter_group.update_from_raw_response(
                    region_db_parameter_group.dict_src
                )
                return db_parameter_group

        response = self.provision_db_parameter_group_raw(db_parameter_group.region,
                                                         db_parameter_group.generate_create_request()
                                                         )
        return db_parameter_group.update_from_raw_response(response)

    def provision_db_parameter_group_raw(self, region, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Creating db_parameter_group: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_db_parameter_group,
                "DBParameterGroup",
                filters_req=request_dict,
        ):
            self.clear_cache(RDSDBParameterGroup)
            return response

    def provision_db_instance(self, db_instance: RDSDBInstance):
        """
        Standard.

        :param db_instance:
        :return:
        """

        try:
            return self.update_db_instance_information(db_instance)
        except self.ResourceNotFoundError:
            pass

        response = self.provision_db_instance_raw(db_instance.region, db_instance.generate_create_request())
        db_instance.update_from_raw_response(response)

        return self.wait_for_status(
            db_instance,
            self.update_db_instance_information,
            [db_instance.Status.AVAILABLE],
            [db_instance.Status.CREATING,
             db_instance.Status.BACKING_UP,
             db_instance.Status.CONFIGURING_LOG_EXPORTS,
             db_instance.Status.CONFIGURING_ENHANCED_MONITORING,
             db_instance.Status.CONFIGURING_IAM_DATABASE_AUTH],
            [db_instance.Status.DELETING, db_instance.Status.FAILED],
            timeout=20 * 60 * 60,
        )

    def provision_db_instance_raw(self, region, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Creating db_instance: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_db_instance, "DBInstance", filters_req=request_dict
        ):
            self.clear_cache(RDSDBInstance)
            return response

    def copy_db_cluster_snapshot(
            self,
            cluster_snapshot_src: RDSDBClusterSnapshot,
            cluster_snapshot_dst: RDSDBClusterSnapshot,
            synchronous=True,
    ):
        """
        Standard.

        :param cluster_snapshot_src:
        :param cluster_snapshot_dst:
        :param synchronous:
        :return:
        """

        filters_req = {"DBClusterSnapshotIdentifier": cluster_snapshot_dst.id}
        dst_region_cluster_snapshots = self.get_region_db_cluster_snapshots(
            cluster_snapshot_dst.region,
            full_information=False,
            custom_filters=filters_req,
        )

        for dst_region_cluster_snapshot in dst_region_cluster_snapshots:
            if dst_region_cluster_snapshot.id == cluster_snapshot_dst.id:
                if (
                        cluster_snapshot_src.arn
                        == dst_region_cluster_snapshot.source_db_cluster_snapshot_arn
                ):
                    cluster_snapshot_dst.update_from_raw_response(
                        dst_region_cluster_snapshot.dict_src
                    )
                    return
                raise RuntimeError(
                    f"Found destination snapshot with name {cluster_snapshot_dst.id} but src arn {dst_region_cluster_snapshot.source_db_cluster_snapshot_arn} is not equals to {cluster_snapshot_src.arn}"
                )

        response = self.copy_db_cluster_snapshot_raw(cluster_snapshot_src.region,
                                                     cluster_snapshot_src.generate_copy_request(cluster_snapshot_dst)
                                                     )
        cluster_snapshot_dst.update_from_raw_response(response)
        if not synchronous:
            return
        start_time = datetime.datetime.now()
        logger.info("Starting waiting loop for cluster_snapshot to become ready")

        timeout = 60 * 60
        sleep_time = 5
        for i in range(timeout // sleep_time):
            filters_req = {"DBClusterSnapshotIdentifier": cluster_snapshot_dst.id}
            dst_region_cluster_snapshots = self.get_region_db_cluster_snapshots(
                cluster_snapshot_dst.region,
                full_information=False,
                custom_filters=filters_req,
            )

            dst_region_cluster_snapshot = dst_region_cluster_snapshots[0]

            if (
                    dst_region_cluster_snapshot.get_status()
                    == dst_region_cluster_snapshot.Status.FAILED
            ):
                raise RuntimeError(
                    f"cluster {dst_region_cluster_snapshot.name} provisioning failed. Cluster in FAILED status"
                )

            if (
                    dst_region_cluster_snapshot.get_status()
                    != dst_region_cluster_snapshot.Status.AVAILABLE
            ):
                logger.info(
                    f"Waiting for snapshot to become available: {i + 1}/{timeout}. "
                    f"Going to sleep for {sleep_time} seconds"
                )
                time.sleep(sleep_time)
                continue

            cluster_snapshot_dst.update_from_raw_response(
                dst_region_cluster_snapshot.dict_src
            )
            end_time = datetime.datetime.now()
            logger.info(f"cluster_snapshot become ready after {end_time - start_time}")
            return

        raise TimeoutError(f"Cluster did not become available for {timeout} seconds")

    def copy_db_cluster_snapshot_raw(self, region, request_dict):
        """
        Copy from region to region.

        :param request_dict:
        :return:
        """

        logger.info(f"Copying cluster_snapshot: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).copy_db_cluster_snapshot,
                "DBClusterSnapshot",
                filters_req=request_dict,
        ):
            self.clear_cache(RDSDBClusterSnapshot)
            return response

    def update_db_cluster_information(self, db_cluster):
        """
        Standard.

        :param db_cluster:
        :return:
        """

        if db_cluster.id is None:
            raise NotImplementedError()
        filters = {"Filters": [{"Name": "db-cluster-id", "Values": [db_cluster.id]}]}
        region_db_clusters = self.get_region_db_clusters(
            db_cluster.region, filters=filters
        )
        if len(region_db_clusters) == 0:
            raise self.ResourceNotFoundError(
                f"db_cluster {db_cluster.id} not found in region {db_cluster.region.region_mark}"
            )

        if len(region_db_clusters) > 1:
            raise RuntimeError(region_db_clusters)

        db_cluster.update_from_raw_response(region_db_clusters[0].dict_src)

    def update_db_instance_information(self, db_instance):
        """
        Standard.

        :param db_instance:
        :return:
        """

        filters_req = {"Filters": [
            {
                "Name": "db-instance-id",
                "Values": [
                    db_instance.id,
                ],
            }
        ]}

        region_db_instances = self.get_region_db_instances(
            db_instance.region, filters=filters_req
        )

        if len(region_db_instances) == 0:
            raise self.ResourceNotFoundError(
                f"db_instance {db_instance.id} not found in region {db_instance.region.region_mark}"
            )

        if len(region_db_instances) > 1:
            raise RuntimeError(region_db_instances)

        db_instance.update_from_raw_response(region_db_instances[0].dict_src)

    def modify_db_cluster(self, db_cluster: RDSDBCluster):
        """
        Standard.

        :param db_cluster:
        :return:
        """

        request = db_cluster.generate_modify_request()
        response = self.modify_db_cluster_raw(db_cluster.region, request)
        db_cluster.update_from_raw_response(response)
        if "MasterUserPassword" in request:
            self.wait_for_status(
                db_cluster,
                self.update_db_cluster_information,
                [db_cluster.Status.RESETTING_MASTER_CREDENTIALS],
                [db_cluster.Status.AVAILABLE],
                [],
                sleep_time=2,
            )
            self.wait_for_status(
                db_cluster,
                self.update_db_cluster_information,
                [db_cluster.Status.AVAILABLE],
                [db_cluster.Status.RESETTING_MASTER_CREDENTIALS],
                [],
            )

    def modify_db_cluster_raw(self, region, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Modifying db_cluster: {request_dict.keys()}")
        for response in self.execute(
                self.get_session_client(region=region).modify_db_cluster, "DBCluster", filters_req=request_dict
        ):
            self.clear_cache(RDSDBCluster)
            return response

    def modify_db_instance(self, db_instance: RDSDBCluster):
        """
        Standard.

        :param db_instance:
        :return:
        """

        response = self.modify_db_instance_raw(db_instance.region, db_instance.generate_modify_request())
        db_instance.update_from_raw_response(response)

    def modify_db_instance_raw(self, region, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Modifying db_instance: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).modify_db_instance, "DBInstance", filters_req=request_dict
        ):
            self.clear_cache(RDSDBInstance)
            return response

    def update_tags(self, objects):
        """
        Standard.

        :param objects:
        :return:
        """

        for obj in objects:
            self.get_tags(obj)

    # pylint: disable= arguments-differ
    def get_tags(self, obj):
        """
        Get tags for object

        :param obj:
        :return:
        """

        tags = list(
            self.execute(
                self.get_session_client(region=obj.region).list_tags_for_resource,
                "TagList",
                filters_req={"ResourceName": obj.arn},
                instant_raise=True
            )
        )
        obj.tags = tags

    def get_default_engine_version(self, region, engine_type):
        """
        Get the default engine in the region.

        :param engine_type:
        :param region:
        :return:
        """

        if per_region := self.ENGINE_VERSIONS.get(region.region_mark):
            if engine_version := per_region.get(engine_type):
                return engine_version

        engine_versions = list(self.execute(
            self.get_session_client(region=region).describe_db_engine_versions, "DBEngineVersions",
            filters_req={"Engine": engine_type, "DefaultOnly": True}))

        if len(engine_versions) != 1:
            raise RuntimeError(f"Can not find single default version for {engine_type} in {str(region)}")

        self.ENGINE_VERSIONS[region.region_mark][engine_type] = engine_versions[0]

        return self.ENGINE_VERSIONS[region.region_mark][engine_type]

    def get_engine_version(self, region, engine_type, engine_version):
        """
        Get the default engine in the region.

        :param engine_type:
        :param region:
        :param engine_version:
        :return:
        """

        all_engine_versions = list(self.execute(
            self.get_session_client(region=region).describe_db_engine_versions, "DBEngineVersions",
            filters_req={"Engine": engine_type, "DefaultOnly": False}))

        engine_versions = [version for version in all_engine_versions if version["EngineVersion"] == engine_version]

        if len(engine_versions) != 1:
            raise RuntimeError(f"Can not find single default version for {engine_type} in {str(region)}")

        self.ENGINE_VERSIONS[region.region_mark][engine_type] = engine_versions[0]

        return self.ENGINE_VERSIONS[region.region_mark][engine_type]

    def describe_db_engine_versions_raw(self, region, filters_req):
        """
        Standard

        :param filters_req:
        :return:
        """

        return list(self.execute(
            self.get_session_client(region=region).describe_db_engine_versions, "DBEngineVersions",
            filters_req=filters_req))

    def get_engine_max_version(self, region, engine_type, raw=False):
        """
        Standard.

        :param region:
        :param engine_type:
        :return:
        """

        lst_all = self.describe_db_engine_versions_raw(region, {"Engine": engine_type, "DefaultOnly": False})
        all_floats = {}
        errors = []
        for eng_version in lst_all:
            try:
                all_floats[float(eng_version["EngineVersion"])] = eng_version
            except ValueError:
                errors.append(eng_version["EngineVersion"])

        max_version = max(all_floats)
        for error_version in errors:
            if error_version.startswith(str(max_version)):
                raise ValueError(f"Can not decide which version is the max version: {max_version=}, {errors=}")

        max_versions = [eng_version_float for eng_version_float in all_floats if eng_version_float == max_version]
        if len(max_versions) != 1:
            raise NotImplementedError(f"{max_versions=}")
        if not raw:
            return max_versions[0]
        return all_floats[max_versions[0]]
