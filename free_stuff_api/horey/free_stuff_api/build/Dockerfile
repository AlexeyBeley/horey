FROM ubuntu:24.04
ARG HOREY_FOLDER_NAME=horey

RUN dnf install -y git make wget which findutils

RUN wget https://bootstrap.pypa.io/get-pip.py

RUN python get-pip.py

RUN rm get-pip.py

RUN dnf install -y atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel nss mesa-libgbm jq unzip


COPY chrome /opt/chrome
COPY chromedriver /opt/chrome-driver
RUN chmod -R 777 /opt/chrome-driver
RUN chmod -R 777 /opt/chrome

RUN dnf install -y vi

COPY frs_api_configuration.json /app

COPY ${HOREY_FOLDER_NAME} /app/horey
RUN python /app/horey/pip_api/horey/pip_api/pip_api_make.py --install horey.free_stuff_api --pip_api_configuration /app/horey/pip_api_docker_configuration.py

COPY lambda_handler.py /app/lambda_handler.py

CMD [ "lambda_handler.handler" ]
