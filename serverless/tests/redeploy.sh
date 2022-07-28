#!/bin/bash

cd ./runtime-tutorial

#layer
zip runtime.zip bootstrap
aws lambda publish-layer-version --region us-west-2 --layer-name bash-runtime --zip-file fileb://runtime.zip


#zip function-only.zip function.sh
#aws lambda update-function-code --region us-west-2 --function-name bash-runtime --zip-file fileb://function-only.zip


aws lambda update-function-configuration --region us-west-2 --function-name bash-runtime \
--layers arn:aws:lambda:us-west-2:1111111111111111:layer:bash-runtime:4

# test:
# aws lambda invoke --region us-west-2 --function-name bash-runtime --payload '{"text":"Hello"}' response.txt --cli-binary-format raw-in-base64-out