#AWS_API - creates datastructures from AWS services.

Menu:
* Installation in a venv 
* Connecting to AWS example 

##############################################################
##Installation in a venv 
```shell
make recursive_install_from_source_local_venv-aws_api
```

Now you can do:

```shell
source build/_build/_venv/bin/activate
#(_venv)
python
#>>> Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08)

from horey.aws_api.aws_api import AWSAPI

AWSAPI
#<class 'horey.aws_api.aws_api.AWSAPI'>
```

###############################################################

##Connecting to AWS example
Use file `aws_api/tests/accounts/default_managed_account.py` to specify what accounts can be accessed by AWS_API.
I use "12345678910".

```python
AWSAccount.ConnectionStep({"profile": "default", "region_mark": "us-east-1"})
...
reg.region_mark = "us-east-1"
```

`AWS credentials` file:
```shell
cat ~/.aws/credentials
[default]
aws_access_key_id = XXXXXXXXXXXXXXXX
aws_secret_access_key = XXXXXXXXXXXXXXXXXXXXXXXXXX
```

###README_AWS_API_CONFIGURATION.md
* Explains how to prepare working environment.

###README_CLEANUP.md
* Explains how to run AWS cleanup utils.


##README_AWS_CLIENTS.md
* Connections' management internals.


#Full flow:
```shell
ubuntu:~$ git clone https://github.com/AlexeyBeley/horey.git
Cloning into 'horey'...
remote: Enumerating objects: 903, done.
remote: Counting objects: 100% (903/903), done.
remote: Compressing objects: 100% (500/500), done.
remote: Total 903 (delta 557), reused 643 (delta 309), pack-reused 0
Receiving objects: 100% (903/903), 209.39 KiB | 20.94 MiB/s, done.
Resolving deltas: 100% (557/557), done.

ubuntu:~$ cd horey/
ubuntu:~/horey$ sudo apt-get update
ubuntu:~/horey$ sudo apt install make
ubuntu:~/horey$ sudo apt-get install python3-venv -y
ubuntu:~/horey$ sudo apt install python3-pip -y

make recursive_install_from_source_local_venv-aws_api

```





#halilit - paam be shavua 265 kinor
#organit - 150 230
#hamishi - 17:00, 
#shlishi - 17:00
#erez
#mifgash 