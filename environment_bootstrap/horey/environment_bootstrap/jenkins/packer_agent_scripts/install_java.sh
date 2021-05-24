#!/bin/bash
set -xe

sudo add-apt-repository -y ppa:openjdk-r/ppa
sudo apt-get update
sudo apt-get install openjdk-11-jdk -y

sudo apt-get install -y git