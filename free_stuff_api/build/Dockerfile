FROM public.ecr.aws/lambda/python:3.12
ARG HOREY_FOLDER_NAME=horey

RUN dnf install -y git make wget which findutils

RUN wget https://bootstrap.pypa.io/get-pip.py

RUN python get-pip.py

RUN rm get-pip.py

RUN dnf install -y \
    atk \
    cups-libs \
    gtk3 \
    libXcomposite \
    alsa-lib \
    libXcursor \
    libXdamage \
    libXext \
    libXi \
    libXrandr \
    libXScrnSaver \
    libXtst \
    pango \
    at-spi2-atk \
    libXt \
    xorg-x11-server-Xvfb \
    xorg-x11-xauth \
    dbus-glib \
    dbus-glib-devel \
    nss \
    mesa-libgbm \
    && dnf clean all

RUN dnf install -y vi

RUN dnf install -y unzip && \
    curl -Lo "/tmp/chromedriver-linux64.zip" "https://storage.googleapis.com/chrome-for-testing-public/145.0.7632.77/linux64/chromedriver-linux64.zip" && \
    curl -Lo "/tmp/chrome-linux64.zip" "https://storage.googleapis.com/chrome-for-testing-public/145.0.7632.77/linux64/chrome-linux64.zip" && \
    unzip /tmp/chromedriver-linux64.zip -d /opt/ && \
    unzip /tmp/chrome-linux64.zip -d /opt/

COPY frs_api_configuration.json ${LAMBDA_TASK_ROOT}

COPY ${HOREY_FOLDER_NAME} ${LAMBDA_TASK_ROOT}/horey
# RUN cd ${LAMBDA_TASK_ROOT}/horey && make recursive_install_from_source-alert_system
RUN python ${LAMBDA_TASK_ROOT}/horey/pip_api/horey/pip_api/pip_api_make.py --install horey.free_stuff_api --pip_api_configuration ${LAMBDA_TASK_ROOT}/horey/pip_api_docker_configuration.py

COPY lambda_handler.py ${LAMBDA_TASK_ROOT}/

CMD [ "lambda_handler.handler" ]
