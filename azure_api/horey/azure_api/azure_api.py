import json
import pdb
from horey.azure_api.azure_clients.compute_client import ComputeClient
from horey.azure_api.azure_clients.resource_groups_client import ResourceGroupsClient
from horey.common_utils.common_utils import CommonUtils
from horey.azure_api.base_entities.azure_account import AzureAccount
from horey.azure_api.azure_service_entities.resource_group import ResourceGroup


class AzureAPI:
    def __init__(self, configuration=None):
        self.compute_client = ComputeClient()
        self.resource_groups_client = ResourceGroupsClient()
        self.resource_groups = []
        self.virtual_machines = []
        self.configuration = configuration
        self.init_configuration()

    def init_configuration(self):
        """
        Sets current active account from configuration
        """
        if self.configuration is None:
            return
        accounts = CommonUtils.load_object_from_module(self.configuration.accounts_file, "main")
        AzureAccount.set_azure_account(accounts[self.configuration.azure_account])

    def init_resource_groups(self):
        objects = self.resource_groups_client.get_all_resoure_groups()
        self.resource_groups += objects

    def cache_objects(self, objects, cache_file_path):
        lst_dicts = [obj.convert_to_dict() for obj in objects]
        with open(cache_file_path, "w+") as file_handler:
            json.dump(lst_dicts, file_handler)

    def deploy_resource_group(self, resource_group):
        self.resource_groups_client.create_resource_group(resource_group)

