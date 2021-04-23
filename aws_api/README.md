# AWS_API - creates datastructures from AWS services

Menu:
* Installation
* Connecting to AWS example 
* Step by step basic flow

## Installation 
After a short prep 
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


## Connecting to AWS example
Use file `aws_api/tests/accounts/default_managed_account.py` to specify what accounts can be accessed by AWS_API.

In the example there is a single account: "12345678910".

#### *For more information about AWS_API configuration goto: [Managing AWS_API configuration](docs/README_AWS_API_CONFIGURATION.md)

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
#### *For more information about connections' configurations goto: [Managing AWS connections](docs/README_CONNECTING_AWS.md)

Use file `aws_api/tests/configuration_values.py` to select current AWSAccount to work with.

I use AWSAccount with ID: "12345678910".

#### *For more information about AWS_API configuration goto: [Managing AWS_API configuration](docs/README_AWS_API_CONFIGURATION.md)


# Step by step basic flow
#### *For more information about other cleanup routines goto: [Cleanup feature usage and examples](docs/README_CLEANUP.md) 
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

ubuntu:~/horey$ mkdir ~/.aws/
ubuntu:~/horey$ vi ~/.aws/credentials
ubuntu:~/horey$ make recursive_install_from_source_local_venv-aws_api

#
# Make your magic here - I am going to use [default] profile and region "us-east-1"
# To change these go to README.md section "Connecting to AWS example"
 
ubuntu:~/horey$ cd aws_api/

ubuntu:~/horey/aws_api$ make aws_api_init_and_cache-interfaces
source /home/ubuntu/horey/aws_api/../build/_build/_venv/bin/activate &&\
export PYTHONPATH=/home/ubuntu/horey/aws_api/horey/aws_api &&\
python3 /home/ubuntu/horey/aws_api/horey/aws_api/aws_api_actor.py --action init_and_cache --target interfaces --configuration_file_full_path /home/ubuntu/horey/aws_api/../aws_api/tests/configuration_values.py
[2021-04-22 08:17:30,761] INFO:configuration_policy.py:82: Init attribute 'aws_api_account' from python file: '/home/ubuntu/horey/aws_api/../aws_api/tests/configuration_values.py'
[2021-04-22 08:17:30,762] INFO:configuration_policy.py:82: Init attribute 'aws_api_cache_dir' from python file: '/home/ubuntu/horey/aws_api/../aws_api/tests/configuration_values.py'
[2021-04-22 08:17:30,762] INFO:configuration_policy.py:82: Init attribute 'accounts_file' from python file: '/home/ubuntu/horey/aws_api/../aws_api/tests/configuration_values.py'
[2021-04-22 08:17:30,776] INFO:sessions_manager.py:49: region_mark: us-east-1 client: ec2
[2021-04-22 08:17:30,852] INFO:sessions_manager.py:49: region_mark: us-east-1 client: ec2
[2021-04-22 08:17:30,858] INFO:boto3_client.py:70: Start paginating with starting_token: 'None' and args '{}'
[2021-04-22 08:17:30,859] INFO:sessions_manager.py:49: region_mark: us-east-1 client: ec2
[2021-04-22 08:17:31,032] INFO:boto3_client.py:99: Updating 'describe_network_interfaces' {} pagination starting_token: None

ubuntu:~/horey/aws_api$ ls -l tests/ignore/cache/12345678910/ec2/network_interfaces.json
-rw-rw-r-- 1 ubuntu ubuntu 20994 Apr 22 08:17 tests/ignore/cache/12345678910/ec2/network_interfaces.json

ubuntu:~/horey/aws_api$ make aws_api_cleanup-interfaces
source /home/ubuntu/horey/aws_api/../build/_build/_venv/bin/activate &&\
python3 /home/ubuntu/horey/aws_api/horey/aws_api/aws_api_actor.py --action cleanup --target interfaces --configuration_file_full_path /home/ubuntu/horey/aws_api/../aws_api/tests/configuration_values.py
[2021-04-22 08:23:54,020] INFO:configuration_policy.py:82: Init attribute 'aws_api_account' from python file: '/home/ubuntu/horey/aws_api/../aws_api/tests/configuration_values.py'
[2021-04-22 08:23:54,020] INFO:configuration_policy.py:82: Init attribute 'aws_api_cache_dir' from python file: '/home/ubuntu/horey/aws_api/../aws_api/tests/configuration_values.py'
[2021-04-22 08:23:54,021] INFO:configuration_policy.py:82: Init attribute 'accounts_file' from python file: '/home/ubuntu/horey/aws_api/../aws_api/tests/configuration_values.py'

ubuntu:~/horey/aws_api$ ls tests/ignore/cache/12345678910/cleanup/network_interfaces.txt
tests/ignore/cache/12345678910/cleanup/network_interfaces.txt

ubuntu:~/horey/aws_api$ cat tests/ignore/cache/12345678910/cleanup/network_interfaces.txt
* Unused network interfaces (0)
```
