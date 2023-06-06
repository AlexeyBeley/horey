FROM ubuntu:22.04

RUN apt-get -qq update\
	&& apt-get install -yqq python3.11 \
	&& ln -s /usr/bin/python3.11 /usr/bin/python

RUN pip3 install awslambdaric

ENV DEBIAN_FRONTEND=noninteractive

COPY app.py app.py

CMD [ "app.handler" ]
