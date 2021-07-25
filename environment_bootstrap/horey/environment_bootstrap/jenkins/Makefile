
CURRENT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PROJECT_ROOT_DIR := ${CURRENT_DIR}/../../../..

CONFIGURATION_DIR_PATH := ${PROJECT_ROOT_DIR}/../ignore/jenkins_deployer
CONFIGURATION_FILE_PATH := ${CONFIGURATION_DIR_PATH}/jenkins_deployer_configuration_values.py

JENKINS_DIR := ${PROJECT_ROOT_DIR}/environment_bootstrap/horey/environment_bootstrap/jenkins
VENV_BIN_DIR := ${PROJECT_ROOT_DIR}/build/_build/_venv/bin

JENKINS_IP_ADDR := 1.1.1.1

JENKINS_MASTER_CONNECTION_STRING := "ubuntu@${JENKINS_IP_ADDR}"
JENKINS_MASTER_KEY_PATH := "/Users/alexey.beley/.ssh/jenkins-key.pem"
RELEASE_CODE_NAME := $(shell lsb_release -cs)

install_make_on_jenkins_master:
	ssh -t -i ${JENKINS_MASTER_KEY_PATH} -o StrictHostKeyChecking=no ${JENKINS_MASTER_CONNECTION_STRING} "sudo apt-get install make -y"

#todo: copy_packer_files_to_jenkins: install_make_on_jenkins_master
copy_packer_files_to_jenkins:
	scp -i ${JENKINS_MASTER_KEY_PATH} -o StrictHostKeyChecking=no ${CURRENT_DIR}/packer.pkr.hcl ${JENKINS_MASTER_CONNECTION_STRING}:/tmp
	scp -i ${JENKINS_MASTER_KEY_PATH} -o StrictHostKeyChecking=no ${CURRENT_DIR}/jenkins_agent_ami.json ${JENKINS_MASTER_CONNECTION_STRING}:/tmp
	scp -i ${JENKINS_MASTER_KEY_PATH} -o StrictHostKeyChecking=no ${CURRENT_DIR}/Makefile ${JENKINS_MASTER_CONNECTION_STRING}:/tmp
	scp -i ${JENKINS_MASTER_KEY_PATH} -o StrictHostKeyChecking=no -r ${CURRENT_DIR}/packer_agent_scripts ${JENKINS_MASTER_CONNECTION_STRING}:/tmp

test:
	echo "${RELEASE_CODE_NAME}"

deploy_infrastructure:
	source ${VENV_BIN_DIR}/activate &&\
	python3 ${JENKINS_DIR}/jenkins_deployer_actor.py --action deploy_infrastructure --configuration_file_full_path ${CONFIGURATION_FILE_PATH}

install-make:
	#todo: Just kidding, but don't forget to do it.
	sudo apt install make

aws_api_cleanup-%:
	source ${VENV_BIN_DIR}/activate &&\
	python3 ${AWS_API_DIR}/aws_api_actor.py --action cleanup --target $(subst aws_api_cleanup-,,$@) --configuration_file_full_path ${CONFIGURATION_FILE_PATH}

install-java:
	sudo apt-get update &&\
	sudo apt-get install openjdk-11-jdk -y

install-jenkins-stable: install-java
	wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add - &&\
	sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list' &&\
	sudo apt-get update &&\
	sudo apt-get install jenkins -y

# Error: these line added to /etc/apt/sources.list and this is wrong.
#deb [arch=amd64] https://apt.releases.hashicorp.com main
## deb-src [arch=amd64] https://apt.releases.hashicorp.com main
#fixing it:
#deb [arch=amd64] https://apt.releases.hashicorp.com bionic main
## deb-src [arch=amd64] https://apt.releases.hashicorp.com bionic main

install-packer:
	curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add - &&\
	sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com ${RELEASE_CODE_NAME} main" &&\
	sudo apt-get update &&\
 	sudo apt-get install packer

uznip-plugin:
	sudo apt-get install -y unzip
	sudo unzip packer-plugin*.zip
	sudo rm packer-plugin-*.zip

init-packer:
	sudo packer init packer.pkr.hcl

run-agent-packer:
	sudo packer build jenkins_agent_ami.json

