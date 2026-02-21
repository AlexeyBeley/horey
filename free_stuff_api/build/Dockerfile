FROM public.ecr.aws/lambda/python:3.12
ARG HOREY_FOLDER_NAME=horey

RUN dnf install -y git make wget which findutils

RUN wget https://bootstrap.pypa.io/get-pip.py

RUN python get-pip.py

RUN rm get-pip.py


COPY ${HOREY_FOLDER_NAME} ${LAMBDA_TASK_ROOT}/horey
# RUN cd ${LAMBDA_TASK_ROOT}/horey && make recursive_install_from_source-alert_system
RUN python ${LAMBDA_TASK_ROOT}/horey/pip_api/horey/pip_api/pip_api_make.py --install horey.free_stuff_api --pip_api_configuration ${LAMBDA_TASK_ROOT}/horey/pip_api_docker_configuration.py

RUN cp ${LAMBDA_TASK_ROOT}/horey/free_stuff_api/horey/free_stuff_api/lambda_package/lambda_handler.py ${LAMBDA_TASK_ROOT}/

CMD [ "lambda_handler.handler" ]
