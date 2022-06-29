FROM ubuntu:bionic

ADD ./app /app
ADD ./provisioners /provisioners

RUN chmod +x ./provisioners/*.sh

RUN ./provisioners/provision.sh

WORKDIR /app
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app"]

EXPOSE 8000