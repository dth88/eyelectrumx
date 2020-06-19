import os
import json
import boto3
import atexit
import logging
import requests
from functools import wraps
from time import time, sleep

from lib import electrum_lib
from lib import electrums

from botocore.exceptions import ClientError
from flask import Flask, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)
logging.basicConfig(filename='logs/flask.log',level=logging.DEBUG)
logging.getLogger('apscheduler').setLevel(logging.DEBUG)


@app.before_first_request
def restore_data_from_aws():
    logging.info('@before_first_request execution started')
    restore_electrums_from_aws()
    restore_explorers_from_aws()
    logging.info('@before_first_request execution finished')


def restore_electrums_from_aws():
    s3_client = boto3.client('s3')
    file_name = 'lib/data/backup_electrums.json'
    bucket = 'rocky-cove-80142'
    object_name = 'backup_electrums.json'
    try:
        s3_client.download_file(bucket, object_name, file_name)
    except ClientError as e:
        logging.error(e)
        logging.info('AWS-S3 electrums download: failure')
        return
    logging.info('AWS-S3 electrums download: success')


def restore_explorers_from_aws():
    s3_client = boto3.client('s3')
    file_name = 'lib/data/backup_explorers.json'
    bucket = 'rocky-cove-80142'
    object_name = 'backup_explorers.json'
    try:
        s3_client.download_file(bucket, object_name, file_name)
    except ClientError as e:
        logging.error(e)
        logging.info('AWS-S3 explorers download: failure')
        return
    logging.info('AWS-S3 explorers download: success')


## TODO: create different json files for adex-mob and adex-pro
## so it would not lock main electrum json with many requests.
### TEMPLATES

@app.route("/")
def main():
    with open('lib/data/backup_electrums.json', 'r') as electrum_urls:
        return render_template('electrums.html', electrum_urls=electrum_urls)


@app.route("/adex-mob")
def filter_mob():
    with open('lib/data/backup_electrums.json', 'r') as electrum_urls:
        return render_template('adex-mob.html', electrum_urls=electrum_urls, adexmob=electrums.adex-mob)


@app.route("/adex-pro")
def filter_pro():
    with open('lib/data/backup_electrums.json', 'r') as electrum_urls:
        return render_template('adex-pro.html', electrum_urls=electrum_urls, adexpro=electrums.adex-pro)


@app.route("/explorers")
def explorers():
    with open('lib/data/backup_explorers.json', 'r') as explorers_urls:
        return render_template('explorers.html', explorers_urls=explorers_urls)


@app.route("/api")
def api():
    return render_template('api-docs.html')


### ENDPOINTS

@app.route('/api/electrums')
def get_all_electrums():
    with open('lib/data/backup_electrums.json', 'r') as electrum_urls:
        return jsonify(electrum_urls)


@app.route('/api/adex-mob')
def get_only_adex_mob_electrums():
    with open('lib/data/backup_electrums.json', 'r') as electrum_urls:
        d = {}
        for coin, urls in electrum_urls.items():
            if coin in electrums.adex-mob:
                d[coin] = urls
        return jsonify(d)


@app.route('/api/adex-pro')
def get_only_adex_pro_electrums():
    with open('lib/data/backup_electrums.json', 'r') as electrum_urls:
        d = {}
        for coin, urls in electrum_urls.items():
            if coin in electrums.adex-pro:
                d[coin] = urls
        return jsonify(d)


@app.route('/api/explorers')
def get_all_explorers():
    with open('lib/data/backup_explorers.json', 'r') as explorers_urls:
        return jsonify(explorers_urls)





### BACKGROUND JOBS


def measure(func):
    @wraps(func)
    def _time_it(*args, **kwargs):
        start = int(round(time() * 1000))
        try:
            return func(*args, **kwargs)
        finally:
            end_ = int(round(time() * 1000)) - start
            logging.info(f"Total execution time for {func.__name__}: {end_ if end_ > 0 else 0} ms")
    return _time_it


@measure
def gather_and_backup_electrums():
    logging.info('started background job: electrums update')
    with open('lib/data/backup_electrums.json', 'rw') as electrum_urls:
        updated_urls = electrum_lib.call_electrums_and_update_status(electrum_urls, electrums.electrum_version_call, electrums.eth_call)
        json.dump(updated_urls, f, indent=4, default=str)
    logging.info('finished background job: electrums update and backup')


@measure
def gather_and_backup_explorers():
    logging.info('started background job: explorers update and backup')
    with open('lib/data/backup_electrums.json', 'rw') as explorers_urls:
        updated_urls = electrum_lib.call_explorers_and_update_status(explorers_urls)
        json.dump(updated_urls, f, indent=4, default=str)
    logging.info('finished background job: explorers update and backup')


def backup_electrums_data_to_aws():
    logging.info('started background job: backup electrums data to aws')
    file_name = 'lib/data/backup_electrums.json'
    bucket = 'rocky-cove-80142'
    object_name = 'backup_electrums.json'

    s3_client = boto3.client('s3')

    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        logging.info('AWS-S3 electrums upload: failure')
        return
    logging.info('AWS-S3 electrums upload: success')


def backup_explorers_data_to_aws():
    logging.info('started background job: backup explorers data to aws')
    file_name = 'lib/data/backup_explorers.json'
    bucket = 'rocky-cove-80142'
    object_name = 'backup_explorers.json'

    s3_client = boto3.client('s3')

    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        logging.info('AWS-S3 explorers upload: failure')
        return
    logging.info('AWS-S3 explorers upload: success')


scheduler = BackgroundScheduler()
scheduler.add_job(func=gather_and_backup_electrums, trigger="interval", seconds=80)
scheduler.add_job(func=gather_and_backup_explorers, trigger="interval", seconds=30)
scheduler.add_job(func=backup_electrums_data_to_aws, trigger="interval", minutes=5)
scheduler.add_job(func=backup_explorers_data_to_aws, trigger="interval", minutes=10)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())



if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=os.environ['PORT'])