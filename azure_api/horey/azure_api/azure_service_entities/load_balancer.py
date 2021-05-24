import pdb

from horey.azure_api.azure_service_entities.azure_object import AzureObject


class LoadBalancer(AzureObject):
    def __init__(self, dict_src, from_cache=False):
        self.name = None
        self.id = None
        self.location = None
        self.tags = {}
        self.resource_group_name = None
        self.frontend_ip_configurations = None
        self.backend_address_pools = None
        self.probes = None
        self.sku = None
        self.load_balancing_rules = None

        super().__init__(dict_src, from_cache=from_cache)

        if from_cache:
            self.init_load_balancer_from_cache(dict_src)
            return

        init_options = {
            "id": self.init_default_attr,
            "name": self.init_default_attr,
            "type": self.init_default_attr,
            "location": self.init_default_attr,
            "tags": self.init_default_attr,
            "sku": self.init_default_attr,
            "etag": self.init_default_attr,
            "frontend_ip_configurations": self.init_default_attr,
            "backend_address_pools": self.init_default_attr,
            "load_balancing_rules": self.init_default_attr,
            "probes": self.init_default_attr,
            "inbound_nat_rules": self.init_default_attr,
            "inbound_nat_pools": self.init_default_attr,
            "outbound_rules": self.init_default_attr,
            "resource_guid": self.init_default_attr,
            "provisioning_state": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def init_load_balancer_from_cache(self, dict_src):
        raise NotImplementedError()

    def construct_fip_id(subscription_id):
        """Build the future FrontEndId based on components name.
        """
        return ('/subscriptions/{}'
                '/resourceGroups/{}'
                '/providers/Microsoft.Network'
                '/loadBalancers/{}'
                '/frontendIPConfigurations/{}').format(
            subscription_id, GROUP_NAME, LB_NAME, FIP_NAME
        )

    def construct_bap_id(subscription_id):
        """Build the future BackEndId based on components name.
        """
        return ('/subscriptions/{}'
                '/resourceGroups/{}'
                '/providers/Microsoft.Network'
                '/loadBalancers/{}'
                '/backendAddressPools/{}').format(
            subscription_id, GROUP_NAME, LB_NAME, ADDRESS_POOL_NAME
        )

    def construct_probe_id(subscription_id):
        """Build the future ProbeId based on components name.
        """
        return ('/subscriptions/{}'
                '/resourceGroups/{}'
                '/providers/Microsoft.Network'
                '/loadBalancers/{}'
                '/probes/{}').format(
            subscription_id, GROUP_NAME, LB_NAME, PROBE_NAME
        )

    def generate_create_request(self):

        return [self.resource_group_name,
                self.name,
                {"location": self.location,
                 "frontend_ip_configurations": self.frontend_ip_configurations,
                 "backend_address_pools": self.backend_address_pools,
                 "probes": self.probes,
                 "load_balancing_rules": self.load_balancing_rules,
                 "sku": self.sku,
                 "tags": self.tags
                 }
                ]

    def update_after_creation(self, load_balancer):
        self.id = load_balancer.id
