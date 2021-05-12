#sudo apt install make

install-java:
	sudo apt-get update &&\
	sudo apt-get install openjdk-11-jdk -y

install-jenkins-stable: install-java
	wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add - &&\
	sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list' &&\
	sudo apt-get install jenkins -y

install-packer:
	#todo: does not work!
	exit 0
	curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
	sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
	sudo apt-get update &&\
 	sudo apt-get install packer

install-packer:
	mkdir packer_tutorial &&\
	cp ami.json packer_tutorial &&\
	cd packer_tutorial &&\
	packer init .

init-packer:
	packer init packer.pkr.hcl
	sudo packer build jenkins_agent_ami.json