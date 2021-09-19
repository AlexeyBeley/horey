# AWS_API configuration

## Upload
### CONS
* S3Client is not thread safe. This means if you want to upload multiple objects - wait for one to finish.

### PROS



* Using AWS profile name.
```python
AWSAccount.ConnectionStep({"profile": "horey_account", "region_mark": "us-east-1"})
```
