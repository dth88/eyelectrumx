import os
import json
import boto3
import atexit
import logging
import requests

from lib import electrum_lib
from lib import electrums

from botocore.exceptions import ClientError
from flask import Flask, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)
s3_client = boto3.client('s3')


def restore_electrums_from_aws():
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
    logging.info('before_first_start execution started')
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


@app.before_first_request
def restore_data_from_aws():
    logging.info('before_first_request execution started')
    restore_electrums_from_aws()
    restore_explorers_from_aws()


@app.route("/")
def main():
    electrum_urls = electrum_lib.restore_electrums_from_backup()
    return render_template('index.html', electrum_urls=electrum_urls)


@app.route("/atomicdex-mobile")
def filter_mobile():
    electrum_urls = electrum_lib.restore_electrums_from_backup()
    return render_template('atomicdex.html', electrum_urls=electrum_urls)


@app.route("/explorers")
def explorers():
    explorers_urls = electrum_lib.restore_explorers_from_backup()
    return render_template('explorers.html', explorers_urls=explorers_urls)


@app.route("/api")
def api():
    return render_template('api-docs.html')


### API CALLS

@app.route('/api/electrums')
def get_all_electrums():
    electrum_urls = electrum_lib.restore_electrums_from_backup()
    return jsonify(electrum_urls)


@app.route('/api/atomicdex-mob')
def get_only_atomicdex_mobile_electrums():
    electrum_urls = electrum_lib.restore_electrums_from_backup()
    d = {}
    for coin, urls in electrum_urls.items():
        if coin in electrums.atomic_dex_mobile:
            d[coin] = urls
    return jsonify(d)


@app.route('/api/explorers')
def get_all_explorers():
    explorers_urls = electrum_lib.restore_explorers_from_backup()
    return jsonify(explorers_urls)



### BACKGROUND JOBS

def gather_and_backup_electrums():
    logging.info('started background job: electrums update')
    electrum_urls = electrum_lib.restore_electrums_from_backup()
    electrum_urls = electrum_lib.call_electrums_and_update_status(electrum_urls, electrums.electrum_version_call, electrums.eth_call)
    electrum_lib.backup_electrums(electrum_urls)
    logging.info('finished background job: electrums update and backup')



def gather_and_backup_explorers():
    logging.info('started background job: explorers update and backup')
    explorers_urls = electrum_lib.restore_explorers_from_backup()
    explorers_urls = electrum_lib.call_explorers_and_update_status(explorers_urls)
    electrum_lib.backup_explorers(explorers_urls)
    logging.info('finished background job: explorers update and backup')


def backup_electrums_data_to_aws():
    logging.info('started background job: backup electrums data to aws')
    file_name = 'lib/data/backup_electrums.json'
    bucket = 'rocky-cove-80142'
    object_name = 'backup_electrums.json'

    if object_name is None:
        object_name = file_name

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

    if object_name is None:
        object_name = file_name

    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        logging.info('AWS-S3 explorers upload: failure')
        return
    logging.info('AWS-S3 explorers upload: success')


scheduler = BackgroundScheduler()
scheduler.add_job(func=gather_and_backup_electrums, trigger="interval", seconds=100)
scheduler.add_job(func=gather_and_backup_explorers, trigger="interval", seconds=150)
scheduler.add_job(func=backup_electrums_data_to_aws, trigger="interval", minutes=5)
scheduler.add_job(func=backup_explorers_data_to_aws, trigger="interval", minutes=7)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())




if __name__ == "__main__":
    logging.basicConfig(filename='logs/flask.log',level=logging.DEBUG)
    app.run(host="0.0.0.0", port=os.environ['PORT'])