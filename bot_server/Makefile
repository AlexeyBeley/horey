SHELL := /bin/bash
AWS_ACCOUNT_ID := $(shell aws sts get-caller-identity --query Account --output text)

CURRENT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
ROOT_DIR := $(realpath ${CURRENT_DIR}/../../)

BUILD_DIR := /tmp/slack_server_build

REGION := us-east-1
CLUSTER_NAME := PlaceHolder
SERVICE_NAME := PlaceHolder


build_image:
	docker build -t slack-server --platform linux/amd64 .


update_artifact: build_image
	aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
	docker tag slack-server:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/slack_bot:latest
	docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/slack_bot:latest

deploy: update_artifact deploy_raw

deploy_raw:
	aws ecs update-service --region ${REGION} --cluster ${CLUSTER_NAME} --service ${SERVICE_NAME} --force-new-deployment


