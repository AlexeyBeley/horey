from horey.deployer.provision_constructor import ProvisionConstructor
import horey.deployer.system_functions.swap

DEPLOYMENT_DIR = "provision_constructor_deployment"


def test_init():
    provision_constructor = ProvisionConstructor(DEPLOYMENT_DIR)
    assert isinstance(provision_constructor, ProvisionConstructor)


def test_add_system_function_swap():
    provision_constructor = ProvisionConstructor(DEPLOYMENT_DIR)
    provision_constructor.add_system_function(horey.deployer.system_functions.swap, ram_size_in_gb=4)

    assert isinstance(provision_constructor, ProvisionConstructor)


if __name__ == "__main__":
    #test_init()
    test_add_system_function_swap()
