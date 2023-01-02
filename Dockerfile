# syntax=docker/dockerfile:1

WORKDIR /app

FROM python:3.8-slim-buster

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "./main.py" ]