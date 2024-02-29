FROM docker:dind

RUN apk add --no-cache aws-cli
RUN mkdir /root/.aws
COPY credentials /root/.aws/credentials
