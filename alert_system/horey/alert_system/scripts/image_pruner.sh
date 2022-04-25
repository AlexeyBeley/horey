#!/bin/bash

set -xe

IMAGE_COUNT=$(sudo docker image ls | wc -l)

if (( $IMAGE_COUNT > 5 )); then
    sudo docker image ls | tail -n +5  | while read line
    do
            image_id=$(echo $line | awk '{print $3 }')
            sudo docker image rm $image_id
    done
fi