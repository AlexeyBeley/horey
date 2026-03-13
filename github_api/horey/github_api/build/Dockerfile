FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    curl \
    sudo \
    git \
    ca-certificates \
    curl \
    libicu-dev &&\
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# Add runner user
RUN useradd -m -s /bin/bash runner && \
    usermod -aG sudo runner && \
    echo "runner ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER runner
WORKDIR /home/runner

# Download and setup GitHub runner
RUN curl -o actions-runner-linux-x64-2.311.0.tar.gz -L \
    https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz && \
    tar xzf actions-runner-linux-x64-2.311.0.tar.gz

COPY entrypoint.sh .

RUN sudo chmod +x ./entrypoint.sh
RUN sudo ./bin/installdependencies.sh
ENTRYPOINT ["./entrypoint.sh"]
