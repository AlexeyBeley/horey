"""
AWS rds client to handle rds service API requests.
"""
import datetime
import pdb
import time

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.rds_db_instance import RDSDBInstance
from horey.aws_api.aws_services_entities.rds_db_cluster import RDSDBCluster
from horey.aws_api.aws_services_entities.rds_db_subnet_group import RDSDBSubnetGroup
from horey.aws_api.aws_services_entities.rds_db_cluster_parameter_group import RDSDBClusterParameterGroup
from horey.aws_api.aws_services_entities.rds_db_cluster_snapshot import RDSDBClusterSnapshot
from horey.aws_api.aws_services_entities.rds_db_parameter_group import RDSDBParameterGroup
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.h_logger import get_logger

logger = get_logger()


class RDSClient(Boto3Client):
    NEXT_PAGE_REQUEST_KEY = "Marker"
    NEXT_PAGE_RESPONSE_KEY = "Marker"
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "rds"
        super().__init__(client_name)

    def get_all_db_instances(self, region=None):
        """
        Get all db_instances in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_db_instances(region)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_db_instances(region)

        return final_result

    def get_region_db_instances(self, region, filters=None):
        final_result = list()
        if filters is not None:
            filters = {"Filters": filters}

        AWSAccount.set_aws_region(region)
        for response in self.execute(self.client.describe_db_instances, "DBInstances", filters_req=filters):
            obj = RDSDBInstance(response)
            final_result.append(obj)

        return final_result

    def get_all_db_clusters(self, region=None):
        """
        Get all db_clusters in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_db_clusters(region)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_db_clusters(region)

        return final_result

    def get_region_db_clusters(self, region, filters=None):
        final_result = list()
        if filters is not None:
            filters = {"Filters": filters}

        AWSAccount.set_aws_region(region)
        for response in self.execute(self.client.describe_db_clusters, "DBClusters", filters_req=filters):
            obj = RDSDBCluster(response)
            final_result.append(obj)

        return final_result

    def provision_db_cluster(self, db_cluster: RDSDBCluster, snapshot_id=None):
        if snapshot_id is not None:
            return self.restore_db_cluster_from_snapshot(db_cluster, snapshot_id)

        region_db_clusters = self.get_region_db_clusters(db_cluster.region)
        for region_db_cluster in region_db_clusters:
            if db_cluster.id == region_db_cluster.id:
                db_cluster.update_from_raw_response(region_db_cluster.dict_src)
                return

        AWSAccount.set_aws_region(db_cluster.region)
        response = self.provision_db_cluster_raw(db_cluster.generate_create_request())
        db_cluster.update_from_raw_response(response)

        self.wait_for_status(db_cluster, self.update_db_cluster_information, [db_cluster.Status.AVAILABLE],
                             [db_cluster.Status.CREATING], [db_cluster.Status.FAILED, db_cluster.Status.DELETING])

    def provision_db_cluster_raw(self, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Creating db_cluster: {request_dict}")
        for response in self.execute(self.client.create_db_cluster, "DBCluster",
                                     filters_req=request_dict):
            return response

    def dispose_db_cluster(self, db_cluster: RDSDBCluster):
        region_db_clusters = self.get_region_db_clusters(db_cluster.region)
        for region_db_cluster in region_db_clusters:
            if db_cluster.id == region_db_cluster.id:
                db_cluster.update_from_raw_response(region_db_cluster.dict_src)
                break
        else:
            return
        filters_req = [{'Name': 'db-cluster-id',
                        'Values': [
                            db_cluster.id,
                        ]}]
        db_instances = self.get_region_db_instances(region=db_cluster.region, filters=filters_req)
        for db_instance in db_instances:
            db_instance.region = db_cluster.region
            db_instance.skip_final_snapshot = db_cluster.skip_final_snapshot
            self.dispose_db_instance(db_instance)

        AWSAccount.set_aws_region(db_cluster.region)
        response = self.dispose_db_cluster_raw(db_cluster.generate_dispose_request())

        db_cluster.update_from_raw_response(response)

        try:
            self.wait_for_status(db_cluster, self.update_db_cluster_information, [],
                                 [db_cluster.Status.DELETING, db_cluster.Status.AVAILABLE], [], timeout=20*60)
        except self.ResourceNotFoundError:
            pass

    def dispose_db_cluster_raw(self, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Disposing db_cluster: {request_dict}")
        for response in self.execute(self.client.delete_db_cluster, "DBCluster",
                                     filters_req=request_dict):
            return response

    def dispose_db_instance(self, db_instance: RDSDBInstance):
        AWSAccount.set_aws_region(db_instance.region)
        response = self.dispose_db_instance_raw(db_instance.generate_dispose_request())

        db_instance.update_from_raw_response(response)

    def dispose_db_instance_raw(self, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Disposing db_instance: {request_dict}")
        for response in self.execute(self.client.delete_db_instance, "DBInstance",
                                     filters_req=request_dict):
            return response

    def restore_db_cluster_from_snapshot(self, db_cluster, snapshot_id):
        AWSAccount.set_aws_region(db_cluster.region)
        response = self.restore_db_cluster_from_snapshot_raw(
            db_cluster.generate_restore_db_cluster_from_snapshot_request(snapshot_id))
        db_cluster.update_from_raw_response(response)

    def restore_db_cluster_from_snapshot_raw(self, request_dict):
        """
        Returns ARN
        """
        logger.info(f"restoring db_cluster from snapshot: {request_dict}")
        for response in self.execute(self.client.restore_db_cluster_from_snapshot, "DBCluster",
                                     filters_req=request_dict):
            return response

    def get_all_db_subnet_groups(self, region=None):
        """
        Get all db_subnet_groups in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_db_subnet_groups(region)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_db_subnet_groups(region)

        return final_result

    def get_region_db_subnet_groups(self, region):
        final_result = list()
        AWSAccount.set_aws_region(region)
        for response in self.execute(self.client.describe_db_subnet_groups, "DBSubnetGroups"):
            obj = RDSDBSubnetGroup(response)
            final_result.append(obj)

        return final_result

    def provision_db_subnet_group(self, db_subnet_group):
        region_db_subnet_groups = self.get_region_db_subnet_groups(db_subnet_group.region)
        for region_db_subnet_group in region_db_subnet_groups:
            if db_subnet_group.name == region_db_subnet_group.name:
                db_subnet_group.update_from_raw_response(region_db_subnet_group.dict_src)
                return

        AWSAccount.set_aws_region(db_subnet_group.region)
        response = self.provision_db_subnet_group_raw(db_subnet_group.generate_create_request())
        db_subnet_group.update_from_raw_response(response)

    def provision_db_subnet_group_raw(self, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Creating db_subnet_group: {request_dict}")
        for response in self.execute(self.client.create_db_subnet_group, "DBSubnetGroup",
                                     filters_req=request_dict):
            return response

    def get_all_db_cluster_parameter_groups(self, region=None):
        """
        Get all db_cluster_parameter_groups in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_db_cluster_parameter_groups(region)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_db_cluster_parameter_groups(region)

        return final_result

    def get_region_db_cluster_parameter_groups(self, region, full_information=True):
        final_result = list()
        AWSAccount.set_aws_region(region)
        for response in self.execute(self.client.describe_db_cluster_parameter_groups, "DBClusterParameterGroups"):
            obj = RDSDBClusterParameterGroup(response)
            final_result.append(obj)
            if full_information:
                filters_req = {"DBClusterParameterGroupName": obj.name}
                obj.parameters = []
                for response_param in self.execute(self.client.describe_db_cluster_parameters, "Parameters",
                                                   filters_req=filters_req):
                    obj.parameters.append(response_param)

        return final_result

    def get_all_db_cluster_snapshots(self, region=None):
        """
        Get all db_cluster_snapshot in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_db_cluster_snapshots(region)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_db_cluster_snapshots(region)

        return final_result

    def get_region_db_cluster_snapshots(self, region, full_information=True, custom_filters=None):
        final_result = list()
        AWSAccount.set_aws_region(region)
        for response in self.execute(self.client.describe_db_cluster_snapshots, "DBClusterSnapshots",
                                     filters_req=custom_filters,
                                     exception_ignore_callback=lambda x: "DBClusterSnapshotNotFoundFault" in repr(x)):
            obj = RDSDBClusterSnapshot(response)
            final_result.append(obj)
            if full_information:
                filters_req = {"DBClusterSnapshotIdentifier": obj.id}
                obj.parameters = []
                for response_param in self.execute(self.client.describe_db_cluster_snapshot_attributes,
                                                   "DBClusterSnapshotAttributesResult", filters_req=filters_req):
                    obj.parameters.append(response_param)

        return final_result

    def get_all_db_parameter_groups(self, region=None):
        """
        Get all db_parameter_groups in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_db_parameter_groups(region)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_db_parameter_groups(region)

        return final_result

    def get_region_db_parameter_groups(self, region, full_information=True):
        final_result = list()
        AWSAccount.set_aws_region(region)
        for response in self.execute(self.client.describe_db_parameter_groups, "DBParameterGroups"):
            obj = RDSDBParameterGroup(response)
            final_result.append(obj)
            if full_information:
                filters_req = {"DBParameterGroupName": obj.name}
                obj.parameters = []
                for response_param in self.execute(self.client.describe_db_parameters, "Parameters",
                                                   filters_req=filters_req):
                    obj.parameters.append(response_param)

        return final_result

    def provision_db_cluster_parameter_group(self, db_cluster_parameter_group):
        region_db_cluster_parameter_groups = self.get_region_db_cluster_parameter_groups(
            db_cluster_parameter_group.region)
        for region_db_cluster_parameter_group in region_db_cluster_parameter_groups:
            if db_cluster_parameter_group.name == region_db_cluster_parameter_group.name:
                db_cluster_parameter_group.update_from_raw_response(region_db_cluster_parameter_group.dict_src)
                return

        AWSAccount.set_aws_region(db_cluster_parameter_group.region)
        response = self.provision_db_cluster_parameter_group_raw(db_cluster_parameter_group.generate_create_request())
        db_cluster_parameter_group.update_from_raw_response(response)

    def provision_db_cluster_parameter_group_raw(self, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Creating db_cluster_parameter_group: {request_dict}")
        for response in self.execute(self.client.create_db_cluster_parameter_group, "DBClusterParameterGroup",
                                     filters_req=request_dict):
            return response

    def provision_db_parameter_group(self, db_parameter_group):
        region_db_parameter_groups = self.get_region_db_parameter_groups(db_parameter_group.region)
        for region_db_parameter_group in region_db_parameter_groups:
            if db_parameter_group.name == region_db_parameter_group.name:
                db_parameter_group.update_from_raw_response(region_db_parameter_group.dict_src)
                return

        AWSAccount.set_aws_region(db_parameter_group.region)
        response = self.provision_db_parameter_group_raw(db_parameter_group.generate_create_request())
        db_parameter_group.update_from_raw_response(response)

    def provision_db_parameter_group_raw(self, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Creating db_parameter_group: {request_dict}")
        for response in self.execute(self.client.create_db_parameter_group, "DBParameterGroup",
                                     filters_req=request_dict):
            return response

    def provision_db_instance(self, db_instance: RDSDBInstance):
        try:
            return self.update_db_instance_information(db_instance)
        except self.ResourceNotFoundError:
            pass

        AWSAccount.set_aws_region(db_instance.region)
        response = self.provision_db_instance_raw(db_instance.generate_create_request())
        db_instance.update_from_raw_response(response)

        self.wait_for_status(db_instance, self.update_db_instance_information, [db_instance.Status.AVAILABLE],
                             [db_instance.Status.CREATING, db_instance.Status.CONFIGURING_LOG_EXPORTS],
                             [db_instance.Status.DELETING, db_instance.Status.FAILED], timeout=20 * 60 * 60)

    def provision_db_instance_raw(self, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Creating db_instance: {request_dict}")
        for response in self.execute(self.client.create_db_instance, "DBInstance",
                                     filters_req=request_dict):
            return response

    def copy_db_cluster_snapshot(self, cluster_snapshot_src: RDSDBClusterSnapshot,
                                 cluster_snapshot_dst: RDSDBClusterSnapshot, synchronous=True):
        AWSAccount.set_aws_region(cluster_snapshot_src.region)

        filters_req = {"DBClusterSnapshotIdentifier": cluster_snapshot_dst.id}
        dst_region_cluster_snapshots = self.get_region_db_cluster_snapshots(cluster_snapshot_dst.region,
                                                                            full_information=False,
                                                                            custom_filters=filters_req)

        for dst_region_cluster_snapshot in dst_region_cluster_snapshots:
            if dst_region_cluster_snapshot.id == cluster_snapshot_dst.id:
                if cluster_snapshot_src.arn == dst_region_cluster_snapshot.source_db_cluster_snapshot_arn:
                    cluster_snapshot_dst.update_from_raw_response(dst_region_cluster_snapshot.dict_src)
                    return
                raise RuntimeError(
                    f"Found destination snapshot with name {cluster_snapshot_dst.id} but src arn {dst_region_cluster_snapshot.source_db_cluster_snapshot_arn} is not equals to {cluster_snapshot_src.arn}")

        AWSAccount.set_aws_region(cluster_snapshot_dst.region)
        response = self.copy_db_cluster_snapshot_raw(cluster_snapshot_src.generate_copy_request(cluster_snapshot_dst))
        cluster_snapshot_dst.update_from_raw_response(response)
        if not synchronous:
            return
        start_time = datetime.datetime.now()
        logger.info(f"Starting waiting loop for cluster_snapshot to become ready")

        timeout = 60 * 60
        sleep_time = 5
        for i in range(timeout // sleep_time):
            filters_req = {"DBClusterSnapshotIdentifier": cluster_snapshot_dst.id}
            dst_region_cluster_snapshots = self.get_region_db_cluster_snapshots(cluster_snapshot_dst.region,
                                                                                full_information=False,
                                                                                custom_filters=filters_req)

            dst_region_cluster_snapshot = dst_region_cluster_snapshots[0]

            if dst_region_cluster_snapshot.get_status() == dst_region_cluster_snapshot.Status.FAILED:
                raise RuntimeError(
                    f"cluster {dst_region_cluster_snapshot.name} provisioning failed. Cluster in FAILED status")

            if dst_region_cluster_snapshot.get_status() != dst_region_cluster_snapshot.Status.AVAILABLE:
                logger.info(
                    f"Waiting for snapshot to become available: {i + 1}/{timeout}. "
                    f"Going to sleep for {sleep_time} seconds")
                time.sleep(sleep_time)
                continue

            cluster_snapshot_dst.update_from_raw_response(dst_region_cluster_snapshot.dict_src)
            end_time = datetime.datetime.now()
            logger.info(f"cluster_snapshot become ready after {end_time - start_time}")
            return

        raise TimeoutError(f"Cluster did not become available for {timeout} seconds")

    def copy_db_cluster_snapshot_raw(self, request_dict):
        logger.info(f"Copying cluster_snapshot: {request_dict}")
        for response in self.execute(self.client.copy_db_cluster_snapshot, "DBClusterSnapshot",
                                     filters_req=request_dict):
            return response

    def update_db_cluster_information(self, db_cluster):
        if db_cluster.id is None:
            raise NotImplementedError()
        filters = [{
            'Name': "db-cluster-id",
            'Values': [
                db_cluster.id
            ]
        }]
        region_db_clusters = self.get_region_db_clusters(db_cluster.region, filters=filters)
        if len(region_db_clusters) == 0:
            raise self.ResourceNotFoundError(
                f"db_cluster {db_cluster.id} not found in region {db_cluster.region.region_mark}")

        if len(region_db_clusters) > 1:
            raise RuntimeError(region_db_clusters)

        db_cluster.update_from_raw_response(region_db_clusters[0].dict_src)

    def update_db_instance_information(self, db_instance):
        filters_req = [{'Name': 'db-instance-id',
                        'Values': [
                            db_instance.id,
                        ]}]

        region_db_instances = self.get_region_db_instances(db_instance.region, filters=filters_req)

        if len(region_db_instances) == 0:
            raise self.ResourceNotFoundError(
                f"db_instance {db_instance.id} not found in region {db_instance.region.region_mark}")

        if len(region_db_instances) > 1:
            raise RuntimeError(region_db_instances)

        db_instance.update_from_raw_response(region_db_instances[0].dict_src)

    def modify_db_cluster(self, db_cluster: RDSDBCluster):
        AWSAccount.set_aws_region(db_cluster.region)

        request = db_cluster.generate_modify_request()
        response = self.modify_db_cluster_raw(request)
        db_cluster.update_from_raw_response(response)
        if "MasterUserPassword" in request:
            self.wait_for_status(db_cluster, self.update_db_cluster_information,
                                 [db_cluster.Status.RESETTING_MASTER_CREDENTIALS], [db_cluster.Status.AVAILABLE], [],
                                 sleep_time=2)
            self.wait_for_status(db_cluster, self.update_db_cluster_information, [db_cluster.Status.AVAILABLE],
                                 [db_cluster.Status.RESETTING_MASTER_CREDENTIALS], [])

    def modify_db_cluster_raw(self, request_dict):
        logger.info(f"Modifying db_cluster: {request_dict.keys()}")
        for response in self.execute(self.client.modify_db_cluster, "DBCluster",
                                     filters_req=request_dict):
            return response

    def modify_db_instance(self, db_instance: RDSDBCluster):
        AWSAccount.set_aws_region(db_instance.region)
        response = self.modify_db_instance_raw(db_instance.generate_modify_request())
        db_instance.update_from_raw_response(response)

    def modify_db_instance_raw(self, request_dict):
        logger.info(f"Modifying db_instance: {request_dict}")
        for response in self.execute(self.client.modify_db_instance, "DBInstance",
                                     filters_req=request_dict):
            return response
