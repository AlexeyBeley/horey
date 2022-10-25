SHELL := /bin/bash

ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

REQUEST := "none"

validate_gitlab_identity:
	python3.8 authorization_job_actor.py --request ${REQUEST}
