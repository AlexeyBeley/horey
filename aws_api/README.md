# aws_api

Configuration:
{
"accounts_file_path": "/ignorme/accounts.py"
}

make install_aws_api
```
python3 aws_api_actor --action cleanup_report --configuration_file_path "./configuration.json"
```
```
python3 aws_api_actor --action cleanup_report --configuration_file_path "./configuration.yaml"
```
```
python3 aws_api_actor --action cleanup_report --accounts_file_path "/ignorme/accounts.json" 
```
```
python3 aws_api_actor --action cleanup_report --accounts_file_path "/ignorme/accounts.py" 
```
```
make aws_api_cleanup-lambda
```