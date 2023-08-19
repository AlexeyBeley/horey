"""
CloudfrontFunction

"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject

# pylint: disable= too-many-instance-attributes
class EC2InstanceType(AwsObject):
    """
    AWS identity representation class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.instance_type = None
        self.current_generation = None
        self.free_tier_eligible = None
        self.supported_usage_classes = None
        self.supported_root_device_types = None
        self.supported_virtualization_types = None
        self.bare_metal = None
        self.hypervisor = None
        self.processor_info = None
        self.v_cpu_info = None
        self.memory_info = None
        self.instance_storage_supported = None
        self.instance_storage_info = None
        self.ebs_info = None
        self.network_info = None
        self.placement_group_info = None
        self.hibernation_supported = None
        self.burstable_performance_supported = None
        self.dedicated_hosts_supported = None
        self.auto_recovery_supported = None
        self.supported_boot_modes = None
        self.nitro_enclaves_support = None
        self.nitro_tpm_support = None
        self.nitro_tpm_info = None
        self.gpu_info = None
        self.inference_accelerator_info = None
        self.fpga_info = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        self.update_from_raw_response(dict_src)

    def _init_object_from_cache(self, dict_src):
        """
        Init from cache
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def update_from_raw_response(self, dict_src):
        """
        Standard.

        :param dict_src:
        :return:
        """

        init_options = {
                        "InstanceType": self.init_default_attr,
                        "CurrentGeneration": self.init_default_attr,
                        "FreeTierEligible": self.init_default_attr,
                        "SupportedUsageClasses": self.init_default_attr,
                        "SupportedRootDeviceTypes": self.init_default_attr,
                        "SupportedVirtualizationTypes": self.init_default_attr,
                        "BareMetal": self.init_default_attr,
                        "Hypervisor": self.init_default_attr,
                        "ProcessorInfo": self.init_default_attr,
                        "VCpuInfo": self.init_default_attr,
                        "MemoryInfo": self.init_default_attr,
                        "InstanceStorageSupported": self.init_default_attr,
                        "InstanceStorageInfo": self.init_default_attr,
                        "EbsInfo": self.init_default_attr,
                        "NetworkInfo": self.init_default_attr,
                        "PlacementGroupInfo": self.init_default_attr,
                        "HibernationSupported": self.init_default_attr,
                        "BurstablePerformanceSupported": self.init_default_attr,
                        "DedicatedHostsSupported": self.init_default_attr,
                        "AutoRecoverySupported": self.init_default_attr,
                        "SupportedBootModes": self.init_default_attr,
                        "NitroEnclavesSupport": self.init_default_attr,
                        "NitroTpmSupport": self.init_default_attr,
                        "NitroTpmInfo": self.init_default_attr,
                        "GpuInfo": self.init_default_attr,
                        "InferenceAcceleratorInfo": self.init_default_attr,
                        "FpgaInfo": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)
