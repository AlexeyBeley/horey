SHELL := /bin/bash

ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

IDENTITY := "none"
JENKINS_JOB_JSON := "none"

validate_gitlab_identity:
	python3.8 authorization_job_actor.py --jenkins_job_json ${JENKINS_JOB_JSON} --identity ${IDENTITY}
