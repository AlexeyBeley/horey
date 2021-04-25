# AWS Cleanup

## Intro
Toolset to perform basic AWS environment cleanup procedures.
A vast majority of the cleanups run on cached data- i.e. needed objects must be explicitly loaded before.
In order to understand which objects must be inited check the `test_aws_api_clenup.py` file.

## Sample flow
### *After you've done the base flow in [Step by step basic flow](../README.md)

Let's take for example this cleanup function from `~/horey/aws_api/tests/test_aws_api_cleanup.py`

```python
@pytest.mark.skip(reason="IAM policies cleanup will be enabled explicitly")
def test_init_from_cache_and_cleanup_report_iam_policies():
    aws_api.init_iam_policies(from_cache=True, cache_file=configuration.aws_api_iam_policies_cache_file)
    aws_api.init_iam_roles(from_cache=True, cache_file=configuration.aws_api_iam_roles_cache_file)
    aws_api.cleanup_report_iam_policies(configuration.aws_api_cleanups_iam_policies_report_file)
```

To run `cleanup_report_iam_policies` we need 2 explicitly preloaded object types: `iam_policies` and `iam_roles`.
We are going to perform the following steps:
* Turning on initiation and caching for IAM Roles and Policies test functions.
* Turning on IAM Roles' and Policies' cleanup test functions.
* Running `init_and_cache` to download IAM Roles and Policies data.
* Running cleanup functions on the downloaded data.

By default, all test functions are disabled by `pytest.mark.skip` decorator.
In order to enable them we comment the decorator: 

```bash
ubuntu:~$ vi horey/aws_api/tests/test_aws_api_init_and_cache.py

#comment the skip test line
@pytest.mark.skip(reason="IAM roles will be inited explicitly")
# --->
#@pytest.mark.skip(reason="IAM roles will be inited explicitly")

@pytest.mark.skip(reason="IAM policies will be inited explicitly")
# ---> 
#@pytest.mark.skip(reason="IAM policies will be inited explicitly")

ubuntu:~$ vi horey/aws_api/tests/test_aws_api_cleanup.py
#comment the skip test line
@pytest.mark.skip(reason="IAM roles cleanup will be enabled explicitly")
# --->
#@pytest.mark.skip(reason="IAM roles cleanup will be enabled explicitly")

@pytest.mark.skip(reason="IAM policies cleanup will be enabled explicitly")
# --->
#@pytest.mark.skip(reason="IAM policies cleanup will be enabled explicitly")

ubuntu:~$ cd horey/aws_api

ubuntu:~/horey/aws_api$ make test_aws_api_init
...
...
tests/test_aws_api_init_and_cache.py ..ssssssssssssss                                                                                                      [100%]

================================================================= 2 passed, 14 skipped in 20.39s =================================================================

ubuntu:~/horey/aws_api$ make test_aws_api_cleanup
tests/test_aws_api_cleanup.py ..sssssss                                                                                                                    [100%]

================================================================== 2 passed, 7 skipped in 0.58s ==================================================================
```

## Currently available cleanups
### EC2 Network Interfaces:
Function cleanup_report_network_interfaces:
Generates report of unused network interfaces.


### Lambdas:
Function cleanup_report_lambdas includes following functions:
* Function cleanup_report_lambdas_not_running - checks relevant cloudwatch streams. 
  If you don't use cloudwatch for lambda logging, this report may be useless.
  
* Function cleanup_report_lambdas_large_size - Lambdas should be kept as small as possible.
  
* Function cleanup_report_lambdas_security_group - Lambdas don't have to be open for connections. 
  If there are open ports, it might be a misconfiguration.

* Function cleanup_report_lambdas_old_code - to old code should be reviewed.


### EC2 Load Balancers
Function cleanup_load_balancers- for both alb and classic:
* No instances associated with these load balancers
* No listeners associated with these load balancers
* No target groups associated with these load balancers
* Function cleanup_target_groups- Target groups with bad health


### EC2 Security Groups
Function cleanup_report_security_groups includes following functions:
* Function cleanup_report_wrong_port_lbs_security_groups - 
  Security group opens ports lb doesn't listen.
  Or security group does not open ports lb listens. 
* Function cleanup_report_unused_security_group- security groups not assigned to any interface.
* Function cleanup_report_dangerous_security_groups- "permit any any" is not owr way!


### S3
Dew to huge amounts of data this report must be used carefully.
Function cleanup_report_s3_buckets_objects flow:
* Function generate_summarised_s3_cleanup_data - we can not store all the data in RAM, so I generate a summarizing file.
* Function cleanup_report_s3_buckets_objects_large - uses previous data to generate report.


### IAM roles:
Function cleanup_report_iam_roles: "Unused IAM roles. Last use time > 30 days"


### IAM Policies:
Function cleanup_report_iam_policies:
* Unused polices.
* Function cleanup_report_iam_policy_statements_optimize_not_statement - to permissive, dangerous policies.
* Function cleanup_report_iam_policy_statements_intersecting_statements - A pilot function to try and catch inconsistencies.  


### Cloudwatch
Function cleanup_report_cloud_watch_log_groups: reports top size log groups. 


### Route53
Function cleanup_report_dns_records: Another pilot. Generates a "map" based on seeds - EC2 instances, S3, EC2 Load Balancers etc.
Reports unknown hosted zones -> records. 
It can point valid resources- DNS records pointing to CDN, DDoS protection, or other external resources. 
