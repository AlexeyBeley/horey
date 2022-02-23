import pdb

from horey.provision_constructor.system_function_factory import SystemFunctionFactory


@SystemFunctionFactory.register
class OutputOpensearch(SystemFunctionFactory.SystemFunction):
    def __init__(self, root_deployment_dir, provisioner_script_name,
                 index_pattern=None,
                 opensearch_host=None,
                 opensearch_user=None,
                 opensearch_password=None):
        pdb.set_trace()

        super().__init__(root_deployment_dir, provisioner_script_name)

        self.move_system_function_to_deployment_dir()

        pdb.set_trace()

        self.add_system_function_to_provisioner_script()

        self.add_system_function_common()
        self.add_system_function_common()
