FROM python:3.12-slim-bookworm

ENV TZ=Etc/UTC
ENV DEBIAN_FRONTEND=noninteractive


COPY . .

RUN python -m pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["python", "horey/bot_server/bot_server.py"]
