FROM public.ecr.aws/lambda/python:3.12
ARG HOREY_FOLDER_NAME=horey
ARG CUSTOM_FILES_FOLDER_NAME=custom_files

RUN dnf install -y git make wget which findutils

RUN wget https://bootstrap.pypa.io/get-pip.py

RUN python get-pip.py

RUN rm get-pip.py
RUN cp ${LAMBDA_TASK_ROOT}/horey/alert_system/horey/alert_system/lambda_package/lambda_handler.py ${LAMBDA_TASK_ROOT}/

CMD [ "lambda_handler.handler" ]
