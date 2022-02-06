REMOTE_ADDRESS := "bastion.development"
REMOTE_DIR := "/tmp/"

scp_code:
	scp -r ./src  ${REMOTE_ADDRESS}:${REMOTE_DIR} &&\
	scp Makefile ${REMOTE_ADDRESS}:${REMOTE_DIR}

build:
	gcc -g -o a.out ./src/*.c

remote_build: scp_code
	ssh ${REMOTE_ADDRESS} "cd ${REMOTE_DIR} && make build"
