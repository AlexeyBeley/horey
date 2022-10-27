SHELL := /bin/bash

ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

REQUEST := "none"

validate_gitlab_identity:
	cd ${ROOT_DIR}/../../../../ && make recursive_install_from_source-jenkins_manager &&\
	echo "${REQUEST}" &&\
	cd ${ROOT_DIR} && python3.8 authorization_job_actor.py --action authorize --request "${REQUEST}"
