FROM python:3.7-alpine

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 80

CMD ["gunicorn", "app:app", "--log-file", "logs/gunicorn.log"]
