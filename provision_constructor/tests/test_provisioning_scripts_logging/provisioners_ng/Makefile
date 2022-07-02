

run:
	git um "debug" &&\
	git push &&\
	ssh -t -i /Users/alexey.beley/.ssh/jenkins-dev-master.pem -o StrictHostKeyChecking=no ubuntu@44.192.112.8 "cd /home/ubuntu/horey/provision_constructor/tests/test_provisioning_scripts_logging/provisioners_ng/ && git pull && sudo provision.sh 1>/home/ubuntu/horey/provision_constructor/tests/test_provisioning_scripts_logging/provisioners_ng/stdout.txt 2>&1"