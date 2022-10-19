#!/bin/bash

set -xe

# Download the binary for your system
sudo rm -rf /usr/local/bin/gitlab-runner
sudo curl -L --output /usr/local/bin/gitlab-runner https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-linux-amd64
# Give it permission to execute
sudo chmod +x /usr/local/bin/gitlab-runner

# Create a GitLab Runner user
sudo useradd --comment 'GitLab Runner' --create-home gitlab-runner --shell /bin/bash || true

# Install and run as a service
sudo gitlab-runner install --user=gitlab-runner --working-directory=/home/gitlab-runner || true
sudo gitlab-runner start

export registered_runners_count="NA"
registered_runners_count=$(sudo gitlab-runner list 2>&1 | grep -c "gitlab-jenkins-runner") || true

if [[ "${registered_runners_count}" -eq 0 ]]
then
  sudo gitlab-runner register \
  --name "gitlab-jenkins-runner" \
  --non-interactive \
  --url "https://gitlab.com/" \
  --registration-token "STRING_REPLACEMENT_GITLAB_REGISTRATION_TOKEN" \
  --maintenance-note "Free-form maintainer notes about this runner" \
  --tag-list "jenkins,development" \
  --executor "shell" \
  --run-untagged="true" \
  --locked="false" \
  --access-level="not_protected"
fi

#make ubuntu18 work
sudo cp bash_logout.sh /home/gitlab-runner/.bash_logout
