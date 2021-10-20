# AWS_API configuration

## Upload
### CONS
* S3Client is not thread safe. This means if you want to upload multiple objects - wait for one to finish.
However, single object can be a directory  


* Using AWS profile name.
```python
AWSAccount.ConnectionStep({"profile": "horey_account", "region_mark": "us-east-1"})
```



Steps:
prepare 

sudo apt install python3.8 python3.8-venv
sudo apt install -y git
sudo apt install -y make
inall-pip

1) Get the code
```bash
git clone https://github.com/AlexeyBeley/horey.git
```

cd ./horey/
make recursive_install_from_source_local_venv-aws_api
cd ./aws_api/tests/
2) Set your bucket name in TEST_BUCKET_NAME variable. 
3) Uncomment the test you want to run in _test_s3_client.py_
For example:
#test_upload_small_file_to_s3()

```bash
make test_s3_client.py
```
    # compare to aws cli 
    # time aws s3 cp --recursive ./test_files_dir s3://horey-alexey-ytest-test
    # time aws s3 cp test_files_dir/test_file s3://horey-alexey-ytest-test