FROM jenkins/jenkins:lts-jdk17

RUN apt update -yqq && apt install -yqq --no-install-recommends \
    source python3 python3-venv python3-pip python-is-python3 && \
    rm -rf /var/lib/apt/lists/*
#USER root
#CMD chown -R jenkins:jenkins /var/jenkins_home

#RUN echo '#!/bin/bash\n\
#set -ex\n\
#whoami\n\
#mkdir -p /var/jenkins_home\n\
#ls -l /var\n\
#chown -R jenkins:jenkins /var/jenkins_home\n\
#exec gosu jenkins /usr/bin/tini -- /usr/local/bin/jenkins.sh "$@"' > /entrypoint.sh
#RUN chmod +x /entrypoint.sh
#RUN chown jenkins:jenkins /entrypoint.sh
USER jenkins

#ENTRYPOINT ["/entrypoint.sh"]
