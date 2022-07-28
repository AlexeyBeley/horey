#!/bin/bash

cd ./runtime-tutorial
chmod 755 function.sh bootstrap

zip function.zip function.sh bootstrap

aws lambda create-function --region us-west-2 --function-name bash-runtime \
--zip-file fileb://function.zip --handler function.handler --runtime provided \
--role arn:aws:iam::111111111111111111:role/role-alexey-cloudwatch-logs

# test:
#aws lambda invoke --region us-west-2 --function-name bash-runtime --payload '{"text":"Hello"}' response.txt --cli-binary-format raw-in-base64-out


#layer
zip runtime.zip bootstrap
aws lambda publish-layer-version --region us-west-2 --layer-name bash-runtime --zip-file fileb://runtime.zip

aws lambda update-function-configuration --region us-west-2 --function-name bash-runtime \
--layers arn:aws:lambda:us-west-2:111111111111111111:layer:bash-runtime:1


zip function-only.zip function.sh
aws lambda update-function-code --region us-west-2 --function-name bash-runtime --zip-file fileb://function-only.zip

# test:
# aws lambda invoke --region us-west-2 --function-name bash-runtime --payload '{"text":"Hello"}' response.txt --cli-binary-format raw-in-base64-out