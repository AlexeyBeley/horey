FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

COPY echo.py /opt/echo.py

ENTRYPOINT ["/usr/local/bin/python3", "/opt/echo.py"]
