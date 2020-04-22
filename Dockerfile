FROM python:3.6-alpine3.11
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt