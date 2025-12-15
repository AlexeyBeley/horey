FROM public.ecr.aws/lambda/python:3.12
ARG HOREY_FOLDER_NAME
ARG CUSTOM_FILES_FOLDER_NAME

COPY alert_system_configuration.json alert_system_configuration.json
COPY lambda_handler.py .
COPY ${CUSTOM_FILES_FOLDER_NAME}/* ${LAMBDA_TASK_ROOT}/
COPY ${HOREY_FOLDER_NAME} ${LAMBDA_TASK_ROOT}/horey

RUN dnf install -y git make wget which findutils

RUN wget https://bootstrap.pypa.io/get-pip.py

RUN python get-pip.py

RUN rm get-pip.py


RUN cd ${LAMBDA_TASK_ROOT}/horey && make recursive_install_from_source-alert_system
WORKDIR ${LAMBDA_TASK_ROOT}

CMD [ "lambda_handler.handler" ]
