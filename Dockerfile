FROM python:3.7

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/app/lib"

EXPOSE 80

CMD ["gunicorn", "app:app", "--log-file", "logs/gunicorn.log"]
