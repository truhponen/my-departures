# syntax=docker/dockerfile:1

ENV APP_DIR=/app
FROM python:3.8-slim-buster

COPY requirements.txt ${APP_DIR}/requirements.txt

RUN pip3 install -r ${APP_DIR}/requirements.txt

COPY . /app

CMD [ "python3", ".${APP_DIR}/main.py" ]