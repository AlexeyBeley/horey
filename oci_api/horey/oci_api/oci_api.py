import json
import pdb
import os
from horey.oci_api.oci_clients.oci_compute_client import OCIComputeClient

from horey.common_utils.common_utils import CommonUtils
from horey.oci_api.base_entities.oci_account import OCIAccount


class OCIAPI:
    def __init__(self, configuration=None):
        self.compute_client = OCIComputeClient()

        self.vm_hosts = []
        
        self.configuration = configuration
        self.init_configuration()

    def init_configuration(self):
        """
        Sets current active account from configuration
        """
        if self.configuration is None:
            return
        accounts = CommonUtils.load_object_from_module(self.configuration.accounts_file, "main")
        OCIAccount.set_oci_account(accounts[self.configuration.oci_account])

    @staticmethod
    def cache_objects(objects, file_name):
        """
        Prepare a cache file from objects.

        @param objects:
        @param file_name:
        @return:
        """
        objects_dicts = [obj.convert_to_dict() for obj in objects]

        if not os.path.exists(os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name))

        with open(file_name, "w") as fil:
            fil.write(json.dumps(objects_dicts))

    def init_vm_hosts(self):
        objects = self.compute_client.get_all_vm_hosts()
        self.vm_hosts = objects
