# Use a Python base image
FROM python:3.9-slim-buster

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    wget \
    unzip \
    libglib2.0-0 \
    libnss3 \
    libgssapi-krb5-2 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the Python script and requirements file
COPY requirements.txt .
COPY your_selenium_script.py .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download and install the Chrome driver
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip -d /usr/local/bin/
RUN chmod +x /usr/local/bin/chromedriver

# Set Chrome options to run in headless mode
ENV CHROME_FLAGS="--no-sandbox --headless --disable-gpu --disable-dev-shm-usage"

# Command to run the Selenium script
CMD ["python", "your_selenium_script.py"]