FROM python-3.6.10

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/app/lib"

EXPOSE 80