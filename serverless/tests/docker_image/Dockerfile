FROM ubuntu:22.04

RUN apt-get -qq update\
	&& apt-get install -yqq python3.11 \
	&& ln -s /usr/bin/python3.11 /usr/bin/python

ENV DEBIAN_FRONTEND=noninteractive

COPY echo.py /opt/echo.py

ENTRYPOINT ["/usr/bin/python", "/opt/echo.py"]
