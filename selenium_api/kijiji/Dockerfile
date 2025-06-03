# Use a lightweight Python base image
FROM python:3.9-slim-buster

# Set environment variables for non-interactive apt-get and locale
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# Install system dependencies required for Chrome and general utilities
# --no-install-recommends helps keep the image size down
RUN apt-get update && \
    apt-get install -y \
    wget \
    unzip \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libdrm-dev \
    libgbm-dev \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxkbcommon0 \
    libxshmfence-dev \
    xdg-utils \
    git-all \
    make \
    libvulkan1 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Download and install Google Chrome Stable
# We use wget to download the .deb package and dpkg to install it.
# The --disable-gpu flag is often needed for headless environments.
RUN wget -q -O /tmp/google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i /tmp/google-chrome-stable_current_amd64.deb || apt-get install -fy && \
    rm /tmp/google-chrome-stable_current_amd64.deb

# Set the working directory inside the container
WORKDIR /app

# Copy the Python requirements file and install dependencies
# --no-cache-dir reduces image size by not storing pip cache
COPY . .
COPY kijiji.json /opt/kijiji.json
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Selenium Python script into the container

# Set environment variables for Chrome to run in headless mode and avoid common issues
# --no-sandbox: Required when running as root in Docker
# --disable-dev-shm-usage: Addresses issues with /dev/shm in some Docker setups
# --headless: Runs Chrome without a GUI
# --disable-gpu: Often required for headless mode
ENV CHROME_OPTIONS="--no-sandbox --headless --disable-gpu --disable-dev-shm-usage"

# Ensure Chrome binary is in PATH for webdriver_manager
ENV PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/google/chrome"

# Command to run your Selenium script when the container starts

RUN git clone https://github.com/AlexeyBeley/horey.git
RUN cd horey && make recursive_install_from_source-h_logger
RUN cd ..


CMD ["python", "check_free.py"]