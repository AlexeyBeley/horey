import pdb
import os

class SystemFunctionFactory:
    REGISTERED_FUNCTIONS = dict()

    @staticmethod
    def register(cls):
        name = cls.__module__
        package_name = name[:name.rfind(".")]
        SystemFunctionFactory.REGISTERED_FUNCTIONS[package_name] = cls

    class SystemFunction:
        def __init__(self, deployment_dir):
            self.deployment_dir = os.path.join(deployment_dir, self.__module__[self.__module__.rfind(".")+1:])

        def mv_self_to_deployment_dir(self, system_function_file_path):
            pdb.set_trace()