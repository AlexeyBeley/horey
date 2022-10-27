
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
BUILD_DIR := ${ROOT_DIR}/build
BUILD_TMP_DIR := ${BUILD_DIR}/_build
VENV_DIR= ${BUILD_TMP_DIR}/_venv

HOREY_ROOT := ${ROOT_DIR}/../..
JENKINS_ACTOR_DIR := ${HOREY_ROOT}/jenkins_manager/horey/jenkins_manager
build_folder:
	mkdir -p ${ROOT_DIR}/_build

init_venv_dir: build_folder
	python3 -m venv ${VENV_DIR}

install_jenkins_manager: init_venv_dir
	source ${VENV_DIR}/bin/activate &&\
	make -f ${HOREY_ROOT}/Makefile recursive_install_from_source-jenkins_manager

commit_and_push:
	git um "fix" &&\
	git push

#reload_job: install_jenkins_manager commit_and_push raw_reload_job
reload_job: install_jenkins_manager raw_reload_job
raw_reload_job:
	source ${VENV_DIR}/bin/activate &&\
	python3 ${JENKINS_ACTOR_DIR}/jenkins_manager_actor.py --action run_job --configuration_file_full_path ${ROOT_DIR}/jenkins_configuration_file.py --build_info_file ${ROOT_DIR}/build_file.json

push_and_reload_job: commit_and_push raw_reload_job

#open 8080
trigger:
	curl -X POST -H "Content-Type: application/json" -H "headerWithNumber: nbr123" -H "headerWithString: a b c" -d '{"action": "closed", "pull_request": { "head": {"ref": "branch_name"}, "statuses_url": "https://api.github.com/repos/alexey-beley/horey/statuses/97da45a4cc1bce01ae0395b33434", "base": {"repo": {"full_name": "horey"} } }}' -vs https://user:password@jenkins_host.com:8080/generic-webhook-trigger/invoke


backup_jobs: install_jenkins_manager raw_backup_jobs
raw_backup_jobs:
	source ${VENV_DIR}/bin/activate &&\
	python3 ${JENKINS_ACTOR_DIR}/jenkins_manager_actor.py --action backup_jobs --configuration_file_full_path ${ROOT_DIR}/jenkins_configuration_file.py --backups_dir ${ROOT_DIR}/backups --jobs_names horey_job

create_jobs: install_jenkins_manager raw_create_jobs
raw_create_jobs:
	source ${VENV_DIR}/bin/activate &&\
	python3 ${JENKINS_ACTOR_DIR}/jenkins_manager_actor.py --action create_jobs --configuration_file_full_path ${ROOT_DIR}/jenkins_configuration_file.py --backups_dir ${ROOT_DIR}/backups/d9builder_falconetix_com --jobs_names Grafana_PR_Tests_1 --overwrite true

#Remove build folders
.PHONY: clear
clear: build_folder
	rm -rf ./_build/*
	rmdir ./_build


test_%: FORCE build
	source ${HOREY_ROOT}/build/_build/_venv/bin/activate &&\
	python3 ${ROOT_DIR}/${@}

FORCE: ;

build:
	cd ${HOREY_ROOT} &&\
	make raw_install_from_source-jenkins_manager
	#make recursive_install_from_source_local_venv-jenkins_manager
