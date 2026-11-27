# horey
My packages.


#Mount drive
docker run --name=nginx -d -v ~/nginxlogs:/var/log/nginx -p 5000:80 nginx

#create image from container
docker commit {container_id} {image_name}
docker run -it --entrypoint=/bin/bash
