import pdb

from horey.provision_constructor.provision_constructor import ProvisionConstructor
import horey.provision_constructor.system_functions.swap
import os

DEPLOYMENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "provision_constructor_deployment")


def test_init():
    provision_constructor = ProvisionConstructor(DEPLOYMENT_DIR)
    assert isinstance(provision_constructor, ProvisionConstructor)


def test_add_system_function_swap():
    provision_constructor = ProvisionConstructor(DEPLOYMENT_DIR, horey_repo_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    provision_constructor.add_system_function("swap", ram_size_in_gb=4)

    assert isinstance(provision_constructor, ProvisionConstructor)


def test_add_system_function_logstash():
    my_dir = os.path.dirname(os.path.abspath(__file__))
    provision_constructor = ProvisionConstructor()
    #provision_constructor.provision_system_function("ntp")
    #provision_constructor.provision_system_function("java")
    provision_constructor.provision_system_function("apt_package", package_name="curl")
    return
    provision_constructor.add_system_function("logrotate", force=True, rotation_path="/var/log/nginx", file_name="nginx")
    provision_constructor.add_system_function("logstash", force=True)
    provision_constructor.add_system_function("logstash.configuration",  pipeline_names=["main"], force=True)
    provision_constructor.add_system_function("logstash.input_file", pipe_name="main", input_file_path="/var/log/test.log", force=True)
    logstash_test_dir = os.path.join(my_dir, "logstash")
    provision_constructor.add_system_function("logstash.filter", pipe_name="main", filter_file_path=os.path.join(logstash_test_dir, "filter.sample"), force=True)
    provision_constructor.add_system_function("logstash.output_file", pipe_name="main", file_path="/var/log/logstash/docker.log", force=True)
    index = "horey-%{+YYYY.MM}"
    provision_constructor.add_system_function("logstash.output_opensearch", pipe_name="main", server_address="1.1.1.1", user="user", password="pass", index=index, force=True)
    provision_constructor.add_system_function("systemd", force=True)
    provision_constructor.add_system_function("systemd.override", service_name="logstash", force=True)
    provision_constructor.add_system_function("logstash.reset_service", trigger_on_any_provisioned=["logstash.input_file",
                                                                             "logstash.filter",
                                                                             "logstash.output_file",
                                                                             "logstash.output_opensearch",
                                                                             "systemd.override"], force=True)
    #docker
    #python3.8
    #zabbix
    #system_journal
    assert isinstance(provision_constructor, ProvisionConstructor)


if __name__ == "__main__":
    #test_init()
    #test_add_system_function_swap()
    test_add_system_function_logstash()
