FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

ENV FLASK_APP=app.py

RUN python -m pip install -r requirements.txt

COPY . .

EXPOSE 8080