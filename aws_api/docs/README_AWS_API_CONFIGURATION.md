#AWS_API configuration.

I use the concept of ConfigurationPolicy.
This is the policy rule set file: `aws_api/horey/aws_api/aws_api_configuration_policy.py`

Components:
* `accounts_file` - full path to managed AWSAccounts' file.
* `aws_api_account` - currently managed AWSAccount ID.
* Directory `ignore`- being ignored by git, so the data or metadata won't be accidentally pushed to repo. 
  I use it to store cache dir for small envs.
* Directory `aws_api_cache_dir`- used to store cache data. Each account_name 
  Tip: if you are going to init S3 objects or Cloudwatch streams- use large size HD or EFS(NFS) 
  because it can go over 1 Terabyte.
* Directory `aws_api_cleanup_reports_dir` - used to store cleanups' output.
