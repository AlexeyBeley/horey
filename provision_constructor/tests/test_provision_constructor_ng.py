"""
Provision constructor tests.
"""

import os
from horey.provision_constructor.provision_constructor import ProvisionConstructor

# pylint: disable = missing-function-docstring
DEPLOYMENT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "provision_constructor_deployment"
)


def test_init():
    provision_constructor = ProvisionConstructor()
    assert isinstance(provision_constructor, ProvisionConstructor)


def test_add_system_function_swap():
    provision_constructor = ProvisionConstructor()
    provision_constructor.add_system_function(
        "swap",
        ram_size_in_gb=4,
        horey_repo_path=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", ".."
        ),
    )

    assert isinstance(provision_constructor, ProvisionConstructor)


def test_add_system_function_logstash():
    my_dir = os.path.dirname(os.path.abspath(__file__))
    provision_constructor = ProvisionConstructor()
    provision_constructor.provision_system_function("ntp")
    provision_constructor.provision_system_function("java")
    provision_constructor.provision_system_function(
        "apt_package_generic", package_name="curl"
    )
    provision_constructor.provision_system_function(
        "apt_package_generic", package_name="apt-transport-https"
    )
    provision_constructor.provision_system_function(
        "apt_package_generic", package_name="ca-certificates"
    )
    provision_constructor.provision_system_function(
        "apt_package_generic", package_name="gnupg"
    )
    provision_constructor.provision_system_function(
        "apt_package_generic", package_name="lsb-release"
    )
    provision_constructor.provision_system_function(
        "apt_package_generic", package_name="make"
    )
    provision_constructor.provision_system_function("npm")
    provision_constructor.provision_system_function("docker")
    provision_constructor.provision_system_function(
        "horey_package_generic",
        package_name="aws_api",
        horey_repo_path="/home/ubuntu/git/horey/",
    )
    provision_constructor.provision_system_function(
        "horey_package_generic",
        package_name="serverless",
        horey_repo_path="/home/ubuntu/git/horey/",
    )
    provision_constructor.provision_system_function(
        "horey_package_generic",
        package_name="network",
        horey_repo_path="/home/ubuntu/git/horey/",
    )
    provision_constructor.provision_system_function(
        "horey_package_generic",
        package_name="deployer",
        horey_repo_path="/home/ubuntu/git/horey/",
    )
    provision_constructor.provision_system_function(
        "horey_package_generic",
        package_name="zabbix_api",
        horey_repo_path="/home/ubuntu/git/horey/",
    )
    provision_constructor.provision_system_function(
        "horey_package_generic",
        package_name="docker_api",
        horey_repo_path="/home/ubuntu/git/horey/",
    )
    provision_constructor.provision_system_function(
        "horey_package_generic",
        package_name="replacement_engine",
        horey_repo_path="/home/ubuntu/git/horey/",
    )
    provision_constructor.provision_system_function(
        "horey_package_generic",
        package_name="azure_api",
        horey_repo_path="/home/ubuntu/git/horey/",
    )
    provision_constructor.add_system_function(
        "logrotate", force=True, rotation_path="/var/log/nginx", file_name="nginx"
    )
    provision_constructor.add_system_function("logstash", force=True)
    provision_constructor.add_system_function(
        "logstash.configuration", pipeline_names=["main"], force=True
    )
    provision_constructor.add_system_function(
        "logstash.input_file",
        pipe_name="main",
        input_file_path="/var/log/test.log",
        force=True,
    )
    logstash_test_dir = os.path.join(my_dir, "logstash")
    provision_constructor.add_system_function(
        "logstash.filter",
        pipe_name="main",
        filter_file_path=os.path.join(logstash_test_dir, "filter.sample"),
        force=True,
    )
    provision_constructor.add_system_function(
        "logstash.output_file",
        pipe_name="main",
        file_path="/var/log/logstash/docker.log",
        force=True,
    )
    index = "horey-%{+YYYY.MM}"
    provision_constructor.add_system_function(
        "logstash.output_opensearch",
        pipe_name="main",
        server_address="1.1.1.1",
        user="user",
        password="pass",
        index=index,
        force=True,
    )
    provision_constructor.add_system_function("systemd", force=True)
    provision_constructor.add_system_function(
        "systemd.override", service_name="logstash", force=True
    )
    provision_constructor.add_system_function(
        "logstash.reset_service",
        trigger_on_any_provisioned=[
            "logstash.input_file",
            "logstash.filter",
            "logstash.output_file",
            "logstash.output_opensearch",
            "systemd.override",
        ],
        force=True,
    )
    assert isinstance(provision_constructor, ProvisionConstructor)


def test_provision_system_function_horey_package_generic_venv():
    """
    python3.8 -m venv ./test_venv

    @return:
    """

    provision_constructor = ProvisionConstructor()
    this_dir = os.path.dirname(os.path.abspath(__file__))
    provision_constructor.provision_system_function(
        "horey_package_generic",
        package_name="jenkins_manager",
        horey_repo_path=os.path.join(this_dir, "..", ".."),
        venv_path=os.path.join(this_dir, "test_venv"),
    )


def test_provision_system_function_pip_api_package_venv():
    """
    python3.8 -m venv ./test_venv

    @return:
    """

    provision_constructor = ProvisionConstructor()
    this_dir = os.path.dirname(os.path.abspath(__file__))
    provision_constructor.provision_system_function(
        "pip_api_package",
        requirements_file_path=os.path.join(
            this_dir, "pip_api_tests_data", "requirements.txt"
        ),
        pip_api_configuration_file=os.path.join(
            this_dir, "pip_api_tests_data", "pip_api_configuration.py"
        ),
    )


if __name__ == "__main__":
    # test_init()
    # test_add_system_function_swap()
    # test_add_system_function_logstash()
    # test_provision_system_function_horey_package_generic_venv()
    test_provision_system_function_pip_api_package_venv()
