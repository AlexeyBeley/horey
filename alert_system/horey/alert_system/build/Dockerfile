FROM public.ecr.aws/lambda/python:3.12

COPY alert_system_configuration.json alert_system_configuration.json
COPY lambda_handler.py .
COPY custom_files/* .

RUN dnf install -y git make wget which findutils

RUN wget https://bootstrap.pypa.io/get-pip.py

RUN python get-pip.py

RUN rm get-pip.py

RUN git clone https://github.com/AlexeyBeley/horey.git
RUN cd horey && make recursive_install_from_source-alert_system
RUN cd ..


CMD [ "lambda_handler.handler" ]
