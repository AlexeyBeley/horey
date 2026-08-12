FROM public.ecr.aws/lambda/python:3.12

RUN dnf install -y git make wget which findutils

RUN wget https://bootstrap.pypa.io/get-pip.py

RUN python get-pip.py

RUN rm get-pip.py

#HOREY_REPOS_END
RUN cp /horey/alert_system/horey/alert_system/lambda_package/lambda_handler.py ${LAMBDA_TASK_ROOT}/

CMD [ "lambda_handler.handler" ]
