FROM jenkins/jenkins:lts-jdk17

#USER root
#CMD chown -R jenkins:jenkins /var/jenkins_home

USER root
RUN echo '#!/bin/bash\n\
set -ex\n\
whoami\n\
mkdir -p /var/jenkins_home\n\
ls -l /var\n\
chown -R jenkins:jenkins /var/jenkins_home\n\
exec gosu jenkins /usr/bin/tini -- /usr/local/bin/jenkins.sh "$@"' > /entrypoint.sh
RUN chmod +x /entrypoint.sh
#RUN chown jenkins:jenkins /entrypoint.sh
#USER jenkins

ENTRYPOINT ["/entrypoint.sh"]
