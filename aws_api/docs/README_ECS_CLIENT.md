


echo "ECS_CLUSTER=horey_new_container_instance" >> /etc/ecs/ecs.config

level=critical time=2021-10-26T16:32:40Z msg="Data mismatch; saved cluster 'horey_container_instance' does not match configured cluster 'horey_new_container_instance'. Perhaps you want to delete the configured checkpoint file?" module=agent.go

sudo rm -rf /var/lib/ecs/data/*


docker logs:
standard_init_linux.go:219: exec user process caused: exec format error

Youv'e built it in arm anf trying to run on amd or the vice versa.

