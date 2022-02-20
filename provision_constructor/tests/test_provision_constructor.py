from horey.provision_constructor.provision_constructor import ProvisionConstructor
import horey.provision_constructor.system_functions.swap
#from horey.provision_constructor.system_functions.swap.check_swap import Check
import os

DEPLOYMENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "provision_constructor_deployment")


def test_init():
    provision_constructor = ProvisionConstructor(DEPLOYMENT_DIR)
    assert isinstance(provision_constructor, ProvisionConstructor)


def test_add_system_function_swap():
    provision_constructor = ProvisionConstructor(DEPLOYMENT_DIR, horey_repo_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    provision_constructor.add_system_function(horey.provision_constructor.system_functions.swap, ram_size_in_gb=4)

    assert isinstance(provision_constructor, ProvisionConstructor)

def test_check_swap():
    check = Check()
    check.check_swap_size()


if __name__ == "__main__":
    #test_init()
    test_add_system_function_swap()
    #test_check_swap()
