# AWS_API configuration.

## AWS_API ConfigurationPolicy
I use the ConfigurationPolicy concept.
This is the aws_api configuration policy file: `aws_api/horey/aws_api/aws_api_configuration_policy.py`

Components:
* `accounts_file` - full path to managed AWSAccounts' file.
* `aws_api_account` - currently managed AWSAccount ID.
* Directory `ignore`- being ignored by git, so the data or metadata won't be accidentally pushed to repo. 
  I use it to store cache dir for small envs.
* Directory `aws_api_cache_dir`- used to store cache data. Each account_name 
  Tip: if you are going to init S3 objects or Cloudwatch streams- use large size HD or EFS(NFS) 
  because it can go over 1 Terabyte.
* Directory `aws_api_cleanup_reports_dir` - used to store cleanups' output.

## AWS_API ConfigurationPolicy Values
This is the aws_api configuration_policy values file.
`aws_api/tests/configuration_values.py`

## HLogger ConfigurationPolicy Values
This is the h_logger configuration_policy values file. 
I use it to log error level messages to `/tmp/error.log`
`aws_api/tests/h_logger_configuration_values.py`
