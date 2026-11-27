from system_function_common import SystemFunctionCommon


class Provisioner(SystemFunctionCommon):
    def __init__(self):
        super().__init__()
        self.validate_provisioned_ancestor = False


if __name__ == "__main__":
    Provisioner.ACTION_MANAGER.call_action()
