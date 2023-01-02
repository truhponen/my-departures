# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

COPY requirements.txt /app/requirements.txt

RUN pip3 install -r /app/requirements.txt

COPY . /app

CMD [ "python3", "./app/main.py" ]