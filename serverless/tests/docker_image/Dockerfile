FROM ubuntu:22.04

RUN apt-get -qq update\
	&& apt-get install -yqq python3.11 curl \
	&& ln -s /usr/bin/python3.11 /usr/bin/python \
	&& curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
	&& python get-pip.py \
	&& rm get-pip.py


RUN python -m pip install awslambdaric

ENV DEBIAN_FRONTEND=noninteractive

COPY app.py app.py

CMD [ "app.handler" ]
