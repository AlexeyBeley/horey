FROM ubuntu:22.04

RUN apt update -qq && apt upgrade -qqy

RUN apt install software-properties-common wget -y

RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt update
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt install python3.10 -y

RUN wget https://bootstrap.pypa.io/get-pip.py

RUN python3.10 get-pip.py

RUN rm get-pip.py

RUN python3.10 -m pip install --upgrade setuptools>=45
RUN python3.10 -m pip install --ignore-installed  flask>=2.0.1

COPY app.py .

ENTRYPOINT ["python3.10", "app.py"]