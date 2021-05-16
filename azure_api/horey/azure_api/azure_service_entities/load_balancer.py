import pdb

from horey.azure_api.azure_service_entities.azure_object import AzureObject


class LoadBalancer(AzureObject):
    def __init__(self, dict_src, from_cache=False):
        self.name = None
        self.id = None
        self.location = None
        self.tags = {}
        self.properties = None

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
        """
        https://github.com/Azure-Samples/network-python-manage-loadbalancer/blob/master/example.py
        frontend_ip_configurations = [{
        'name': FIP_NAME,
        'private_ip_allocation_method': 'Dynamic',
        'public_ip_address': {
            'id': public_ip_info.id
        }
        }]
        GROUP_NAME,
        LB_NAME,
        {
            'location': LOCATION,
            'frontend_ip_configurations': frontend_ip_configurations,
            'backend_address_pools': backend_address_pools,
            'probes': probes,
            'load_balancing_rules': load_balancing_rules,
            'inbound_nat_rules': inbound_nat_rules
        }
        """
        frontend_ip_configurations = [{
            'name': FIP_NAME,
            'private_ip_allocation_method': 'Dynamic',
            'public_ip_address': {
                'id': public_ip_info.id
            }
        }]
        backend_address_pools = [{
            'name': ADDRESS_POOL_NAME
        }]
        probes = [{
            'name': PROBE_NAME,
            'protocol': 'Http',
            'port': 80,
            'interval_in_seconds': 15,
            'number_of_probes': 4,
            'request_path': 'healthprobe.aspx'
        }]
        load_balancing_rules = [{
            'name': LB_RULE_NAME,
            'protocol': 'tcp',
            'frontend_port': 80,
            'backend_port': 80,
            'idle_timeout_in_minutes': 4,
            'enable_floating_ip': False,
            'load_distribution': 'Default',
            'frontend_ip_configuration': {
                'id': self.construct_fip_id(subscription_id)
            },
            'backend_address_pool': {
                'id': self.construct_bap_id(subscription_id)
            },
            'probe': {
                'id': self.construct_probe_id(subscription_id)
            }
        }]
        inbound_nat_rules = [{
            'name': NETRULE_NAME_1,
            'protocol': 'tcp',
            'frontend_port': FRONTEND_PORT_1,
            'backend_port': BACKEND_PORT,
            'enable_floating_ip': False,
            'idle_timeout_in_minutes': 4,
            'frontend_ip_configuration': {
                'id': self.construct_fip_id(subscription_id)
            }
        }]
        return [self.name,
                {"location": self.location,
                 "frontend_ip_configurations": frontend_ip_configurations,
                 "backend_address_pools": backend_address_pools,
                 "probes": probes,
                 "load_balancing_rules": load_balancing_rules,
                 "inbound_nat_rules": inbound_nat_rules,
                 "tags": self.tags
                 }
                ]

    def update_after_creation(self, load_balancer):
        pdb.set_trace()
        self.id = load_balancer.id
        self.properties = load_balancer.properties.__dict__
