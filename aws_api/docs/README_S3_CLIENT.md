# AWS_API configuration

## Upload
### CONS
* S3Client is not thread safe. This means if you want to upload multiple objects - wait for one to finish.
However, single object can be a directory  


###Basic example steps
0.1) Preparation (Ubuntu) \
    ```bash
    sudo apt update
    sudo apt install -y python3.8 python3.8-venv
    sudo apt install -y git
    sudo apt install -y make
    ```\
0.2) Validate you have [default] profile in _~/.aws/credentials_


1) Get the code
    ```bash
    git clone https://github.com/AlexeyBeley/horey.git
    ```

2) Provision application infrastructure
    ```bash
    cd ./horey/
    make install-pip
    make recursive_install_from_source_local_venv-aws_api
    ```

3) Run the tests:
    ```bash
    cd ./aws_api/tests/
    ```
    * Set your bucket name in TEST_BUCKET_NAME variable in _test_s3_client.py_ file. 
    * Uncomment the test you want to run in _test_s3_client.py_ file.
    * For example: #test_upload_small_file_to_s3() -> test_upload_small_file_to_s3() 

    ```bash
    make test_s3_client.py
    ```

4) Cleanup.\
   You don't want to manually delete the 100,000 object from S3, right?\
   Comment all. Uncomment _test_delete_bucket_objects_
   #### #test_delete_bucket_objects() -> test_delete_bucket_objects()
    ```bash
    make test_s3_client.py
    ```

You can compare the result with AWS CLI:
single file:
time aws s3 cp test_files_dir/test_file s3://horey-test-bucket
directory:
time aws s3 cp --recursive ./test_files_dir s3://horey-test-bucket