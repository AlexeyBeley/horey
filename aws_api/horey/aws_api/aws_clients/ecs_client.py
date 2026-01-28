"""
ECS client to handle ECS api calls

"""

# pylint: disable= too-many-lines

import copy
import datetime
import time

from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.aws_api.aws_services_entities.ecs_cluster import ECSCluster
from horey.aws_api.aws_services_entities.ecs_service import ECSService
from horey.aws_api.aws_services_entities.ecs_task import ECSTask
from horey.aws_api.aws_services_entities.ecs_capacity_provider import (
    ECSCapacityProvider,
)
from horey.aws_api.aws_services_entities.ecs_task_definition import ECSTaskDefinition
from horey.aws_api.aws_services_entities.ecs_container_instance import (
    ECSContainerInstance,
)

from horey.h_logger import get_logger

logger = get_logger()


class ECSClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    curl 169.254.170.2$AWS_CONTAINER_CREDENTIALS_RELATIVE_URI

    """

    NEXT_PAGE_REQUEST_KEY = "nextToken"
    NEXT_PAGE_RESPONSE_KEY = "nextToken"

    def __init__(self, aws_account=None):
        client_name = "ecs"
        super().__init__(client_name, aws_account=aws_account)

    def run_task(self, region, request_dict):
        """
        Standard

        :param region:
        :param request_dict:
        :return:
        """

        for response in self.execute(
                self.get_session_client(region=region).run_task, "tasks", filters_req=request_dict
        ):
            return response

    def start_task(self, region, request_dict):
        """
        Standard

        :param region:
        :param request_dict:
        :return:
        """

        for response in self.execute(
                self.get_session_client(region=region).start_task, "tasks", filters_req=request_dict
        ):
            return response

    def get_all_clusters(self, region=None):
        """
        Get all clusters in all regions.
        :return:
        """

        return list(self.yield_clusters(region=region))

    def yield_capacity_providers(self, region=None, update_info=False, filters_req=None):
        """
        Yield tables

        :return:
        """

        regional_fetcher_generator = self.yield_capacity_providers_raw

        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            ECSCapacityProvider,
                                                            update_info=update_info,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_capacity_providers_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
            self.get_session_client(region=region).describe_capacity_providers, "capacityProviders", filters_req=filters_req
        )

    def get_all_capacity_providers(self, region=None):
        """
        Get all capacity_providers in all regions.
        :return:
        """

        return list(self.yield_capacity_providers(region=region))

    def get_region_capacity_providers(self, region):
        """
        Standard

        :param region:
        :return:
        """

        return list(self.yield_capacity_providers(region=region))

    def yield_clusters(self, region=None, update_info=False, filters_req=None):
        """
        Yield over all clusters.

        :return:
        """

        regional_fetcher_generator = self.yield_clusters_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            ECSCluster,
                                                            update_info=update_info,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_clusters_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        cluster_identifiers = list(self.execute(
            self.get_session_client(region=region).list_clusters, "clusterArns", filters_req=filters_req
        ))

        if len(cluster_identifiers) > 100:
            raise NotImplementedError(
                """clusters (list) -- A list of up to 100 cluster names or full cluster
            Amazon Resource Name (ARN) entries. If you do not specify a cluster, the default cluster is assumed."""
            )

        filter_req = {
            "clusters": cluster_identifiers,
            "include": [
                "ATTACHMENTS",
                "CONFIGURATIONS",
                "SETTINGS",
                "STATISTICS",
                "TAGS",
            ],
        }

        yield from self.execute(
            self.get_session_client(region=region).describe_clusters, "clusters", filters_req=filter_req
        )

    def get_region_clusters(self, region, cluster_identifiers=None):
        """
        Standard

        :param region:
        :param cluster_identifiers: Cluster name or ARN
        :return:
        """

        region_clusters = list(self.yield_clusters(region=region))
        if cluster_identifiers is None:
            return region_clusters

        return [region_cluster for region_cluster in region_clusters if
                region_cluster.name in cluster_identifiers or region_cluster.arn in cluster_identifiers]

    def dispose_capacity_provider(self, capacity_provider: ECSCapacityProvider):
        """
        Standard.

        @param capacity_provider:
        :return:
        """

        if not self.update_capacity_provider_information(capacity_provider):
            return True

        for cluster in self.get_region_clusters(capacity_provider.region):
            if capacity_provider.name in cluster.capacity_providers:
                self.attach_capacity_providers_to_ecs_cluster(cluster,
                                                              [provider_name for provider_name in
                                                               cluster.capacity_providers
                                                               if provider_name != capacity_provider.name],
                                                              [dict_cap for dict_cap in
                                                               cluster.default_capacity_provider_strategy
                                                               if
                                                               dict_cap["capacityProvider"] != capacity_provider.name])
        ret = self.dispose_capacity_provider_raw(capacity_provider.region,
                                                 capacity_provider.generate_dispose_request()
                                                 )
        status = ret["updateStatus"]

        timeout = 300
        sleep_time = 5
        for _ in range(timeout // sleep_time):
            if status == "DELETE_FAILED":
                raise ValueError(capacity_provider.update_status_reason)
            if status == "DELETE_COMPLETE":
                return True
            if status != "DELETE_IN_PROGRESS":
                raise ValueError(f"{status}: {capacity_provider.update_status_reason}")
            logger.info(f"Waiting for capacity provider deletion. Going to sleep for {sleep_time} sec")
            time.sleep(sleep_time)
            if not self.update_capacity_provider_information(capacity_provider):
                return True
            status = capacity_provider.update_status

        raise TimeoutError(f"Waiting for capacity provider disposal: {timeout} seconds")

    def provision_capacity_provider(self, capacity_provider: ECSCapacityProvider):
        """
        Provision capacity provider

        @param capacity_provider:
        @return:
        """

        region_objects = self.get_region_capacity_providers(capacity_provider.region)
        for region_object in region_objects:
            if region_object.name == capacity_provider.name:
                capacity_provider.update_from_raw_response(region_object.dict_src)
                return

        response = self.provision_capacity_provider_raw(capacity_provider.region,
                                                        capacity_provider.generate_create_request()
                                                        )
        capacity_provider.update_from_raw_response(response)

    def update_capacity_provider_information(self, capacity_provider):
        """
        Standard.

        :param capacity_provider:
        :return:
        """

        region_objects = self.get_region_capacity_providers(capacity_provider.region)
        for region_object in region_objects:
            if region_object.name == capacity_provider.name:
                capacity_provider.update_from_raw_response(region_object.dict_src)
                return True
        return False

    def provision_capacity_provider_raw(self, region, request_dict):
        """
        Standard

        :param request_dict:
        :return:
        """

        logger.info(f"Creating ECS Capacity Provider: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_capacity_provider,
                "capacityProvider",
                filters_req=request_dict,
        ):
            self.clear_cache(ECSCapacityProvider)
            return response

    def dispose_capacity_provider_raw(self, region, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Disposing ECS Capacity Provider: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).delete_capacity_provider,
                "capacityProvider",
                filters_req=request_dict,
        ):
            self.clear_cache(ECSCapacityProvider)
            return response

    def provision_cluster(self, cluster: ECSCluster):
        """
        self.get_session_client(region=region).delete_cluster(capacityProvider='test-capacity-provider')
        """
        existing_cluster = ECSCluster({})
        existing_cluster.name = cluster.name
        existing_cluster.region = cluster.region

        if not self.update_cluster_information(
                existing_cluster) or existing_cluster.get_status() == existing_cluster.Status.INACTIVE:
            response = self.provision_cluster_raw(cluster.region, cluster.generate_create_request())
            cluster.update_from_raw_response(response)
        elif existing_cluster.get_status() == existing_cluster.Status.ACTIVE:
            request = existing_cluster.generate_capacity_providers_request(cluster)
            if request:
                self.attach_capacity_providers_to_ecs_cluster_raw(cluster.region, request)
            return self.update_cluster_information(cluster)

        timeout = 300
        sleep_time = 5
        for _ in range(timeout // sleep_time):
            self.update_cluster_information(cluster)
            if cluster.get_status() == cluster.Status.FAILED:
                cluster.print()
                raise RuntimeError(
                    f"cluster {cluster.name} provisioning failed. Cluster in FAILED status"
                )

            if cluster.get_status() != cluster.Status.ACTIVE:
                time.sleep(sleep_time)
                continue
            return None
        raise TimeoutError(f"Cluster did not become available for {timeout} seconds")

    def provision_cluster_raw(self, region, request_dict):
        """
        Standard

        :param request_dict:
        :return:
        """
        logger.info(f"Creating ECS Capacity Provider: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_cluster, "cluster", filters_req=request_dict
        ):
            self.clear_cache(ECSCluster)
            return response

    def get_all_services(self, cluster=None, region=None):
        """
        Standard

        :param cluster:
        :param region:
        :return:
        """

        filters_req = {"cluster": cluster.name} if cluster else None
        return list(self.yield_services(filters_req=filters_req, region=cluster.region if cluster else region))

    @staticmethod
    def services_cache_filter_callback(filters_req):
        """
        Generate suffix

        :param filters_req:
        :return:
        """
        supported_filters = ["cluster", "region"]
        for key in filters_req:
            if key not in supported_filters:
                raise ValueError(f"{key} is not one of {supported_filters}")

        if "/" not in filters_req["cluster"]:
            return filters_req["cluster"]

        if "arn" in filters_req["cluster"]:
            return filters_req["cluster"].split("/")[-1]

        raise ValueError(filters_req)

    def yield_services(self, region=None, update_info=False, filters_req=None):
        """
        Yield over all services.

        :return:
        """
        regions = [region] if region is not None else AWSAccount.get_aws_account().regions.values()
        regional_fetcher_generator = self.yield_services_raw
        for _region in regions:
            clusters = [filters_req["cluster"]] if filters_req is not None and "cluster" in filters_req else \
                [cluster.arn for cluster in list(self.yield_clusters(region=_region, update_info=update_info))]
            for cluster in clusters:
                filters_req_new = copy.deepcopy(filters_req) if filters_req is not None else {}
                filters_req_new["cluster"] = cluster
                yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                                    ECSService,
                                                                    update_info=update_info,
                                                                    regions=[_region],
                                                                    filters_req=filters_req_new,
                                                                    cache_filter_callback=self.services_cache_filter_callback)

    def yield_services_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """
        task_arns = list(
            self.execute(self.get_session_client(region=region).list_services, "serviceArns", filters_req=filters_req))

        if len(task_arns) == 0:
            return []

        final_result = []
        for i in range(len(task_arns) // 10 + 1):
            filters_req_new = {"services": task_arns[i * 10: (i + 1) * 10], "include": ["TAGS"],
                               "cluster": filters_req["cluster"]}

            if len(filters_req_new["services"]) == 0:
                break

            for dict_src in self.execute(
                    self.get_session_client(region=region).describe_services, "services", filters_req=filters_req_new
            ):
                yield dict_src
                final_result.append(dict_src)

        if len(task_arns) != len(final_result):
            raise RuntimeError(f"{len(task_arns)=} {len(final_result)=}")

        return final_result

    @staticmethod
    def tasks_cache_filter_callback(filters_req):
        """
        Generate suffix

        :param filters_req:
        :return:
        """
        supported_filters = ["cluster", "region"]
        for key in filters_req:
            if key not in supported_filters:
                raise ValueError(f"{key} is not one of {supported_filters}")

        if "/" not in filters_req["cluster"]:
            return filters_req["cluster"]

        if "arn" in filters_req["cluster"]:
            return filters_req["cluster"].split("/")[-1]

        raise ValueError(filters_req)

    def update_task_information(self, task:ECSTask):
        """
        Standard.

        :param task:
        :return:
        """

        final_result = []
        filters_req = {"cluster": task.cluster_arn, "tasks": [task.arn], "include": ["TAGS"]}

        for dict_src in self.execute(
                    self.get_session_client(region=task.region).describe_tasks, "tasks", filters_req=filters_req
            ):
            final_result.append(ECSTask(dict_src))

        if len(final_result) != 1:
            return False

        task.update_from_attrs(final_result[0])
        return True

    def yield_tasks(self, region=None, update_info=False, filters_req=None):
        """
        Yield over all tasks.

        :return:
        """
        regions = [region] if region is not None else AWSAccount.get_aws_account().regions.values()
        regional_fetcher_generator = self.yield_tasks_raw
        for _region in regions:
            clusters = [filters_req["cluster"]] if filters_req is not None and "cluster" in filters_req else \
                [cluster.arn for cluster in list(self.yield_clusters(region=_region, update_info=update_info))]
            for cluster in clusters:
                filters_req_new = copy.deepcopy(filters_req) if filters_req is not None else {}
                filters_req_new["cluster"] = cluster
                yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                                    ECSTask,
                                                                    update_info=update_info,
                                                                    regions=[_region],
                                                                    filters_req=filters_req_new,
                                                                    cache_filter_callback=self.tasks_cache_filter_callback)

    def yield_tasks_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """
        task_arns = list(
            self.execute(self.get_session_client(region=region).list_tasks, "taskArns", filters_req=filters_req))

        if len(task_arns) == 0:
            return []

        final_result = []
        for i in range(len(task_arns) // 100 + 1):
            filters_req_new = {"tasks": task_arns[i * 100: (i + 1) * 100], "include": ["TAGS"],
                               "cluster": filters_req["cluster"]}

            for dict_src in self.execute(
                    self.get_session_client(region=region).describe_tasks, "tasks", filters_req=filters_req_new
            ):
                yield dict_src
                final_result.append(dict_src)

        if len(task_arns) != len(final_result):
            raise RuntimeError(f"{len(task_arns)=} {len(final_result)=}")

        return final_result

    def get_all_tasks(self, region=None):
        """
        Standard

        :param region:
        :return:
        """

        return list(self.yield_tasks(region=region))

    def get_region_tasks(self, region, cluster_name=None, custom_list_filters=None):
        """
        Get region tasks.

        :param region:
        :param cluster_name:
        :param custom_list_filters:
        :return:
        """

        if cluster_name is not None:
            return self.get_cluster_tasks(region, cluster_name, custom_list_filters)

        final_result = []
        for cluster in self.get_region_clusters(region):
            final_result += self.get_cluster_tasks(region, cluster.name, custom_list_filters)

        return final_result

    def get_cluster_tasks(self, region, cluster_name, custom_list_filters):
        """
        Standard

        :param cluster_name:
        :param custom_list_filters:
        :return:
        """

        task_arns = []
        if custom_list_filters is None:
            custom_list_filters = {}
        custom_list_filters["cluster"] = cluster_name

        for arn in self.execute(self.get_session_client(region=region).list_tasks, "taskArns",
                                filters_req=custom_list_filters):
            task_arns.append(arn)

        if len(task_arns) == 0:
            return []

        final_result = []
        for i in range(len(task_arns) // 100 + 1):
            filters_req = {"cluster": cluster_name, "tasks": task_arns[i * 100: (i + 1) * 100], "include": ["TAGS"]}

            for dict_src in self.execute(
                    self.get_session_client(region=region).describe_tasks, "tasks", filters_req=filters_req
            ):
                final_result.append(ECSTask(dict_src))

        if len(task_arns) != len(final_result):
            raise RuntimeError(f"Cluster:{cluster_name} {len(task_arns)=} {len(final_result)=}")
        return final_result

    def get_all_task_definitions(self, region=None):
        """
        Standard

        :param region:
        :return:
        """

        return list(self.yield_task_definitions(region=region))

    def get_region_task_definitions(self, region, family_prefix=None):
        """
        Standard

        :param region:
        :param family_prefix:
        :return:
        """

        filters_req = {"familyPrefix": family_prefix} if family_prefix is not None else None
        return list(self.yield_task_definitions(region=region, filters_req=filters_req))

    def yield_task_definitions(self, region=None, update_info=False, filters_req=None):
        """
        Yield over all task_definitions.

        :return:
        """

        regional_fetcher_generator = self.yield_task_definitions_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            ECSTaskDefinition,
                                                            update_info=update_info,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_task_definitions_raw_old(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        arns = list(self.execute(
            self.get_session_client(region=region).list_task_definitions, "taskDefinitionArns", filters_req=filters_req
        ))

        if len(arns) == 0:
            return []

        for arn in arns:
            filters_req = {"taskDefinition": arn, "include": ["TAGS"]}
            yield from self.execute(
                self.get_session_client(region=region).describe_task_definition, "taskDefinition",
                filters_req=filters_req
            )

        return []

    def yield_task_definitions_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """
        arns = list(self.execute(
            self.get_session_client(region=region).list_task_definitions, "taskDefinitionArns", filters_req=filters_req
        ))

        if len(arns) == 0:
            return []

        for arn in arns:
            filters_req = {"taskDefinition": arn, "include": ["TAGS"]}
            yield from self.execute(
                self.get_session_client(region=region).describe_task_definition, "taskDefinition",
                filters_req=filters_req
            )

        return []

    def provision_ecs_task_definition(self, task_definition: ECSTaskDefinition):
        """
        Standard

        :param task_definition:
        :return:
        """

        response = self.provision_ecs_task_definition_raw(task_definition.region,
                                                          task_definition.generate_create_request()
                                                          )
        task_definition.update_from_raw_response(response)

    def provision_ecs_task_definition_raw(self, region, request_dict):
        """
        Standard

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Creating ECS task definition: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).register_task_definition,
                "taskDefinition",
                filters_req=request_dict,
        ):
            self.clear_cache(ECSTaskDefinition)
            return response

    @staticmethod
    def get_cluster_from_arn(cluster_arn):
        """
        Generate empty named cluster

        :param cluster_arn:
        :return:
        """

        cluster = ECSCluster({})
        cluster.name = cluster_arn.split(":")[-1].split("/")[-1]
        cluster.arn = cluster_arn
        cluster.region = Region.get_region(cluster_arn.split(":")[3])
        return cluster

    def update_service_information(self, service: ECSService):
        """
        Update service info if exists.

        @param service:
        @return:
        """

        if not service.cluster_arn:
            raise ValueError("cluster_arn was not set")

        filters_req = {"cluster": service.cluster_arn, "services": [service.arn]}

        for response in self.execute(
                self.get_session_client(region=service.region).describe_services,
                "services",
                filters_req=filters_req
        ):
            service.update_from_raw_response(response)
            return True

        return False

    def provision_service(self, service: ECSService, asyncronous=False, wait_timeout=10 * 60):
        """
        Standard

        :param asyncronous:
        :param wait_timeout:
        :param service:
        :return:
        """

        cluster = self.get_cluster_from_arn(service.cluster_arn)
        self.clear_cache(ECSService)
        region_objects = self.get_all_services(cluster=cluster)
        for region_object in region_objects:
            if region_object.name == service.name:
                request = region_object.generate_update_request(service)
                if request:
                    response = self.update_service_raw(service.region, request)
                    service.update_from_raw_response(response)
                else:
                    self.update_service_information(service)
                break
        else:
            response = self.create_service_raw(service.region, service.generate_create_request())
            service.update_from_raw_response(response)

        if not asyncronous:
            self.wait_for_deployment_end(service, timeout=wait_timeout)

    def wait_for_deployment_end(self, service, timeout=10 * 60):
        """
        Wait for deployment to end.

        :param timeout: Seconds
        :param service:
        :return:
        """

        self.wait_for_status(service,
                             self.update_service_information,
                             [service.Status.ACTIVE],
                             [service.Status.INACTIVE],
                             [service.Status.DRAINING])

        start_time = datetime.datetime.now()
        datetime_limit = start_time + datetime.timedelta(seconds=timeout)
        last_running_count = 0
        while datetime.datetime.now() < datetime_limit:
            self.update_service_information(service)
            deployments = [ECSService.Deployment(dict_src) for dict_src in service.deployments]
            for deployment in deployments:
                if deployment.status == "PRIMARY":
                    break
            else:
                raise ValueError("No primary deployment")

            if deployment.rollout_state == "COMPLETED":
                logger.info(f"Deployed '{service.name}' in {datetime.datetime.now() - start_time}")
                return True

            if deployment.rollout_state == "IN_PROGRESS":
                if last_running_count < deployment.running_count:
                    last_running_count = deployment.running_count
                    datetime_limit = datetime.datetime.now() + datetime.timedelta(seconds=timeout)

                sleeping_time = min(6, (deployment.desired_count + 1 - deployment.running_count)) * 10
                logger.info(f"Deploying '{service.name}' [{deployment.running_count}/{deployment.desired_count}]. "
                            f"Going to sleep for {sleeping_time} seconds")
                time.sleep(sleeping_time)
                continue

            raise ValueError(f"Unknown deployment rollout state: {deployment.rollout_state}")

        raise TimeoutError(f"Reached timeout: {timeout} seconds")

    def create_service_raw(self, region, request_dict):
        """
        Standard

        :param request_dict:
        :return:
        """

        logger.info(f"Creating ECS Service: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_service, "service", filters_req=request_dict
        ):
            self.clear_cache(ECSService)
            return response

    def update_service_raw(self, region, request_dict):
        """
        Standard

        :param request_dict:
        :return:
        """

        logger.info(f"Updating ECS Service: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).update_service, "service", filters_req=request_dict
        ):
            self.clear_cache(ECSService)
            return response

    def dispose_service(self, cluster, service: ECSService):
        """
        Standard

        :param cluster:
        :param service:
        :return:
        """
        service.cluster_arn = cluster.arn
        self.dispose_service_raw(cluster.region, service.generate_dispose_request(cluster))

    def dispose_service_raw(self, region, request_dict):
        """
        Delete service

        :param request_dict:
        :return:
        """

        logger.info(f"Disposing ECS Service: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).delete_service, "service", filters_req=request_dict,
                exception_ignore_callback=lambda error: "ServiceNotFoundException" in repr(
                    error) or "ClusterNotFoundException" in repr(error)
        ):
            self.clear_cache(ECSService)
            return response

    def dispose_task_definition(self, task_definition):
        """
        Standard.

        :param task_definition:
        :return:
        """
        request_dict = {"taskDefinitions": [f"{task_definition.family}:{task_definition.revision}"]}
        logger.info(f"Disposing ECS Task Definistion: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=task_definition.region).delete_task_definitions, "taskDefinitions",
                filters_req=request_dict
        ):
            logger.info(response)
        return True

    def get_region_container_instances(self, region, cluster_identifier=None):
        """
        Standard

        :param region:
        :param cluster_identifier:
        :return:
        """

        if cluster_identifier is None:
            cluster_identifiers = []
            for cluster_arn in self.execute(self.get_session_client(region=region).list_clusters, "clusterArns"):
                cluster_identifiers.append(cluster_arn)
        else:
            cluster_identifiers = [cluster_identifier]

        final_result = []

        for _cluster_identifier in cluster_identifiers:
            cluster_container_instances_arns = []
            filter_req = {"cluster": _cluster_identifier, "maxResults": 100}

            for container_instance_arn in self.execute(
                    self.get_session_client(region=region).list_container_instances,
                    "containerInstanceArns",
                    filters_req=filter_req
            ):
                cluster_container_instances_arns.append(container_instance_arn)

            if len(cluster_container_instances_arns) == 0:
                continue

            filter_req = {
                "cluster": _cluster_identifier,
                "containerInstances": cluster_container_instances_arns,
                "include": ["TAGS"],
            }

            for dict_src in self.execute(
                    self.get_session_client(region=region).describe_container_instances,
                    "containerInstances",
                    filters_req=filter_req,
            ):
                obj = ECSContainerInstance(dict_src)
                final_result.append(obj)

        return final_result

    def yield_container_instances(self, region=None, update_info=False, filters_req=None):
        """
        Yield tables

        :return:
        """

        regional_fetcher_generator = self.yield_container_instances_raw

        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            ECSContainerInstance,
                                                            update_info=update_info,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_container_instances_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        if filters_req is None:
            filters_req = {}

        if "cluster" not in filters_req:
            cluster_identifiers = list(self.execute(self.get_session_client(region=region).list_clusters, "clusterArns"))
        else:
            cluster_identifiers = [filters_req["cluster"]]

        for _cluster_identifier in cluster_identifiers:
            filters_req.update({"cluster": _cluster_identifier, "maxResults": 100})

            cluster_container_instances_arns = list(self.execute(
                    self.get_session_client(region=region).list_container_instances,
                    "containerInstanceArns",
                    filters_req=filters_req
            ))

            if len(cluster_container_instances_arns) == 0:
                continue

            if len(cluster_container_instances_arns) == 100:
                raise NotImplementedError("Pagination over list_container_instances")

            filter_req = {
                "cluster": _cluster_identifier,
                "containerInstances": cluster_container_instances_arns,
                "include": ["TAGS", "CONTAINER_INSTANCE_HEALTH"],
            }

            yield from self.execute(
                    self.get_session_client(region=region).describe_container_instances,
                    "containerInstances",
                    filters_req=filter_req,
            )

    def dispose_cluster(self, cluster: ECSCluster):
        """
        response = client.deregister_container_instance(
         cluster='string',
        containerInstance='string',
        force=True|False
        )
        @param cluster:
        @return:
        """

        cluster_container_instances = self.get_region_container_instances(
            cluster.region, cluster_identifier=cluster.name
        )
        self.dispose_container_instances(cluster_container_instances, cluster)
        self.dispose_cluster_raw(cluster.region, cluster.generate_dispose_request())

    def dispose_cluster_raw(self, region, request_dict):
        """
        Standard

        :param request_dict:
        :return:
        """

        logger.info(f"Disposing ECS Cluster: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).delete_cluster, "cluster", filters_req=request_dict,
                exception_ignore_callback=lambda error: "ClusterNotFoundException" in repr(error)
        ):
            self.clear_cache(ECSCluster)
            return response

    def dispose_container_instances(self, container_instances, cluster):
        """
        Derefister multiple instances

        :param container_instances:
        :param cluster:
        :return:
        """
        for container_instance in container_instances:
            self.dispose_container_instance_raw(container_instance.region,
                                                container_instance.generate_dispose_request(cluster)
                                                )

    def dispose_container_instance_raw(self, region, request_dict):
        """
        Deregister

        :param request_dict:
        :return:
        """

        logger.info(f"Disposing ECS container instance: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).deregister_container_instance,
                "containerInstance",
                filters_req=request_dict,
        ):
            self.clear_cache(ECSContainerInstance)
            return response

    def dispose_tasks(self, tasks, cluster_name):
        """
        Stop tasks

        :param tasks:
        :param cluster_name:
        :return:
        """

        for task in tasks:
            for response in self.execute(
                    self.get_session_client(region=tasks[0].region).stop_task,
                    "task",
                    filters_req={"cluster": cluster_name, "task": task.arn},
            ):
                logger.info(response)

    def attach_capacity_providers_to_ecs_cluster(
            self, ecs_cluster, capacity_provider_names, default_capacity_provider_strategy
    ):
        """
        Standard

        :param ecs_cluster:
        :param capacity_provider_names:
        :param default_capacity_provider_strategy:
        :return:
        """

        request_dict = {
            "cluster": ecs_cluster.name,
            "capacityProviders": capacity_provider_names,
            "defaultCapacityProviderStrategy": default_capacity_provider_strategy,
        }
        self.attach_capacity_providers_to_ecs_cluster_raw(ecs_cluster.region, request_dict)

    def attach_capacity_providers_to_ecs_cluster_raw(self, region, request_dict):
        """
        Standard

        :param request_dict:
        :return:
        """

        logger.info(f"Attaching capacity provider to ecs cluster: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).put_cluster_capacity_providers,
                "cluster",
                filters_req=request_dict,
        ):
            self.clear_cache(ECSCapacityProvider)
            self.clear_cache(ECSCluster)
            return response

    def update_cluster_information(self, cluster: ECSCluster):
        """
        Standard.

        :param cluster:
        :return:
        """

        ret = self.get_region_clusters(cluster.region, cluster_identifiers=[cluster.name])
        if len(ret) != 1:
            return False

        cluster.update_from_raw_response(ret[0].dict_src)
        return True

    def update_container_instances_information(self, container_instance: ECSContainerInstance):
        """
        Standard.

        :param container_instance:
        :return:
        """

        for region_container_instance in self.get_region_container_instances(container_instance.region,
                                                                             cluster_identifier=container_instance.cluster_name):
            if region_container_instance.arn == container_instance.arn:
                container_instance.update_from_raw_response(region_container_instance.dict_src)
                return True
        return False

    def update_container_instances_state(self, container_instances):
        """
        Desired `status` must be set to the same value for all container_instances.

        :param container_instances:
        :return:
        """

        region = container_instances[0].region
        status = container_instances[0].status

        for container_instance in container_instances:
            if container_instance.region != region:
                raise ValueError(container_instance.region)
            if container_instance.status != status:
                raise ValueError(container_instance.status)

        filters_req = {"cluster": container_instances[0].cluster_name,
                       "status": status
                       }

        ret = []
        for instances_chunk in [container_instances[i:i + 10] for i in range(0, len(container_instances), 10)]:
            filters_req["containerInstances"] = [container_instance.arn for container_instance in instances_chunk]
            ret += self.update_container_instances_state_raw(region, filters_req)

        if status != "DRAINING":
            return ret

        timeout_time = datetime.datetime.now() + datetime.timedelta(minutes=40)
        while datetime.datetime.now() < timeout_time:
            for container_instance in container_instances:
                self.update_container_instances_information(container_instance)
                if container_instance.running_tasks_count > 0:
                    logger.info(
                        f"Container instance {container_instance.ec2_instance_id} tasks: {container_instance.running_tasks_count}")
                    break
            else:
                return ret
            logger.info("Waiting for all container instances to drain going to sleep for 5 sec")
            time.sleep(5)

        raise TimeoutError("Waiting for all container instances to drain")

    def update_container_instances_state_raw(self, region, dict_request):
        """
        Standard.

        :param dict_request:
        :return:
        """

        logger.info(f"Updating container instances states: {dict_request}")
        return list(
            self.execute(self.get_session_client(region=region).update_container_instances_state, "containerInstances",
                         filters_req=dict_request))
