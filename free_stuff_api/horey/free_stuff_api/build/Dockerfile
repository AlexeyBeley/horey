FROM ubuntu:24.04
ARG HOREY_FOLDER_NAME=horey

RUN apt-get update -yqq && apt-get upgrade -yqq
RUN apt-get install -y git make wget which findutils
RUN apt install -y vim
RUN apt install -y libatk1.0-0 libcups2 libgtk-3-0 libxcomposite1 libasound2t64 \
    libxcursor1 libxdamage1 libxext6 libxi6 libxrandr2 libxss1 \
    libxtst6 libpango-1.0-0 libatk-bridge2.0-0 libxt6 xvfb \
    xauth libdbus-glib-1-2 libnss3 libgbm1 jq unzip


RUN apt-get install -y python3-pip python3-full
RUN ln -s /usr/bin/python3 /usr/bin/python

COPY chrome /app/chrome
COPY chromedriver /app/chrome-driver
RUN chmod -R 777 /app/chrome-driver
RUN chmod -R 777 /app/chrome

COPY free_stuff_api_config.json free_stuff_api_config.json
RUN mv free_stuff_api_config.json /opt/free_stuff_api_config.json

COPY hfrs.sqlite hfrs.sqlite
RUN mkdir -p /opt/hfrs/
RUN mv hfrs.sqlite /opt/hfrs/hfrs.sqlite

COPY ${HOREY_FOLDER_NAME} /app/horey
RUN python /app/horey/pip_api/horey/pip_api/pip_api_make.py --install horey.free_stuff_api --pip_api_configuration /app/horey/pip_api_docker_configuration.py

COPY ./horey/free_stuff_api/horey/free_stuff_api/free_stuff_api_actor.py /app/free_stuff_api_actor.py
WORKDIR /app 
CMD ["python", "free_stuff_api_actor.py", "--action", "run_server", "--free_stuff_api_config_file_path", "/opt/free_stuff_api_config.json"]
