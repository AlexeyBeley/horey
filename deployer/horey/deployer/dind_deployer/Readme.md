







#-v /host/directory:/container/directory
docker build -t horey_deployer_image:latest . 
docker run -v ./inseption_dockerfile:/opt/inseption_dockerfile --privileged -d --name horey_deployer horey_deployer_image:latest


docker kill horey_deployer
docker rm horey_deployer

docker exec -it horey_deployer /bin/sh /opt/inseption_dockerfile/deployer.sh 
