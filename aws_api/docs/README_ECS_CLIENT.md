


echo "ECS_CLUSTER=horey_new_container_instance" >> /etc/ecs/ecs.config

level=critical time=2021-10-26T16:32:40Z msg="Data mismatch; saved cluster 'horey_container_instance' does not match configured cluster 'horey_new_container_instance'. Perhaps you want to delete the configured checkpoint file?" module=agent.go

sudo rm -rf /var/lib/ecs/data/*


docker logs:
standard_init_linux.go:219: exec user process caused: exec format error
Youv'e built it in arm anf trying to run on amd or the vice versa.


docker container start dead_man_name
docker container restart dead_man_name
docker logs 
    raise CredentialRetrievalError(provider=self.METHOD,
botocore.exceptions.CredentialRetrievalError: Error when retrieving credentials from container-role: Error retrieving metadata: Received non 200 response (400) from ECS metadata: {"code":"InvalidIdInRequest","message":"CredentialsV2Request: Credentials not found","HTTPErrorCode":400}

cat /var/log/ecs/ecs-agent.log

Unknown eventType: GetCredentialsInvalidRoleType


#Run stopped container /bin/bash
docker commit $CONTAINER_ID user/test_image
docker run -ti --entrypoint=/bin/bash user/test_image


tcpdump -n -i eth0  &
aws s3 ls
09:35:51.160470 IP 172.17.0.3.45178 > 169.254.170.2.80: Flags [P.], seq 144:287, ack 364, win 237, options [nop,nop,TS val 1064800444 ecr 199376951], length 143: HTTP: GET /v2/credentials/3cafd53a-ecdf-4a79-9d03-85a923fb3dbc HTTP/1.1
09:35:51.160890 IP 169.254.170.2.80 > 172.17.0.3.45178: Flags [P.], seq 364:727, ack 287, win 243, options [nop,nop,TS val 199377954 ecr 1064800444], length 363: HTTP: HTTP/1.1 400 Bad Request
Error when retrieving credentials from container-role: Error retrieving metadata: Received non 200 response (400) from ECS metadata: {"code":"InvalidIdInRequest","message":"CredentialsV2Request: Credentials not found","HTTPErrorCode":400}



curl http://169.254.169.254/latest/meta-data/identity-credentials/ec2/security-credentials/ec2-instance

https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html
curl 169.254.170.2$AWS_CONTAINER_CREDENTIALS_RELATIVE_URI

https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-agent-config.html

cat /var/log/ecs/ecs-init.log
2021-10-28T13:41:33Z [INFO] Cleaning up the credentials endpoint setup for Amazon Elastic Container Service Agent
docker container restart 494d361f48f
level=info time=2021-10-28T20:07:17Z msg="Successfully got ECS instance credentials from provider: EC2RoleProvider" module=instancecreds.go