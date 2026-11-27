

docker build -t mufasa:latest .

# Attached:
docker run -p 9090:9090 mufasa:latest

# Detached:
docker run -p 9090:9090 -td mufasa:latest