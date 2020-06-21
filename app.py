import os
import sys
import json
import boto3
import atexit
import logging
import requests
from functools import wraps
from time import time, sleep

from lib import electrum_lib
from lib import electrums

from json import JSONDecodeError
from botocore.exceptions import ClientError
from flask import Flask, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
#logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logging.getLogger('apscheduler').setLevel(logging.DEBUG)


@app.before_first_request
def restore_data_from_aws():
    logging.info('@before_first_request execution started')
    restore_electrums_from_aws()
    restore_explorers_from_aws()
    logging.info('@before_first_request execution finished')


def restore_electrums_from_aws():
    file_name = 'backup_electrums.json'
    bucket = 'rocky-cove-80142'
    object_name = 'backup_electrums.json'

    s3_client = boto3.client('s3')
    try:
        response = s3_client.download_file(bucket, object_name, file_name)
        logging.info(response)
    except ClientError as e:
        logging.error(e)
        logging.error('AWS-S3 electrums DOWNLOAD: FAILURE')
        return False
    logging.info('AWS-S3 electrums DOWNLOAD: SUCCESS')
    return True


def restore_explorers_from_aws():
    file_name = 'backup_explorers.json'
    bucket = 'rocky-cove-80142'
    object_name = 'backup_explorers.json'

    s3_client = boto3.client('s3')
    try:
        response = s3_client.download_file(bucket, object_name, file_name)
        logging.info(response)
    except ClientError as e:
        logging.error(e)
        logging.error('AWS-S3 explorers DOWNLOAD: FAILURE')
        return False
    logging.info('AWS-S3 explorers DOWNLOAD: SUCCESS')
    return True


## TODO: create additional json files for adex-mob and adex-pro
## so it would not lock main electrum json with many requests.


### TEMPLATES
@app.route("/")
def main():
    with open('backup_electrums.json') as electrum_urls:
        electrumz = json.load(electrum_urls)
    return render_template('electrums.html', urlz=electrumz)


@app.route("/adex-mob")
def filter_mob():
    with open('backup_electrums.json') as electrum_urls:
        electrumz = json.load(electrum_urls)
    return render_template('adex-mob.html', urlz=electrumz, adexmob=electrums.adex_mob)


@app.route("/adex-pro")
def filter_pro():
    with open('backup_electrums.json') as electrum_urls:
        electrumz = json.load(electrum_urls)
    return render_template('adex-pro.html', urlz=electrumz, adexpro=electrums.adex_pro)


@app.route("/explorers")
def explorers():
    with open('backup_explorers.json') as explorers_urls:
        explorerz = json.load(explorers_urls)
    return render_template('explorers.html', urlz=explorerz)


@app.route("/api")
def api():
    return render_template('api-docs.html')



### ENDPOINTS

@app.route('/api/electrums')
def get_all_electrums():
    with open('backup_electrums.json') as electrum_urls:
        #electrum_urls = electrum_urls.read()
        #electrum_urls = electrum_urls[:-1]
        electrumz = json.load(electrum_urls)
        return jsonify(electrumz)


@app.route('/api/adex-mob')
def get_adex_mob_electrums():
    with open('backup_electrums.json') as electrum_urls:
        #electrum_urls = electrum_urls.read()
        #electrum_urls = electrum_urls[:-1]
        electrumz = json.load(electrum_urls)
        d = {}
        for coin, urls in electrumz.items():
            if coin in electrums.adex_mob:
                d[coin] = urls
        return jsonify(d)


@app.route('/api/adex-pro')
def get_adex_pro_electrums():
    with open('backup_electrums.json') as electrum_urls:
        electrumz = json.load(electrum_urls)
        d = {}
        for coin, urls in electrumz.items():
            if coin in electrums.adex_pro:
                d[coin] = urls
        return jsonify(d)


@app.route('/api/explorers')
def get_all_explorers():
    with open('backup_explorers.json') as explorers_urls:
        explorerz = json.load(explorers_urls)
        return jsonify(explorerz)



### BACKGROUND JOBS FOR SCHEDULER

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
    logging.info('STARTED background job: ELECTRUMS UPDATE')
    try:
        with open('backup_electrums.json') as electrum_urls:
            electrumz = json.load(electrum_urls)
    # There's an AUTOMAGICAL bug here which happens randomly that I cant get my head around. 
    # It is concatenating one additional curly brace at the end of 'backup_electrums.json'
    # and making it unable to load as json file(raise JSONDecodeError("Extra data", s, end)
    # app[web.1]: json.decoder.JSONDecodeError: Extra data: line 2578 column 2 (char 74668)
    # i was able to fix it only with removing this last curly brace basically "by hands" 
    # if Internal Server Error 500 happens, it is most likely because of this bug.
    # The "funniest" thing that it only happens in HEROKU environment, cant reproduce anywhere else... 
    except JSONDecodeError as e:
        logging.error(e)
        logging.debug("removing last curly brace and trying again")
        with open('backup_electrums.json') as electrum_urls:
            electrumz = electrum_urls.read()
        electrumz = electrumz[:-1]
        electrumz = json.loads(electrumz)

    updated_urls = electrum_lib.call_electrums_and_update_status(electrumz, electrums.electrum_version_call, electrums.eth_call)

    with open('backup_electrums.json', 'w') as f:
        json.dump(updated_urls, f, indent=4)
    logging.info('background job: ELECTRUMS UPDATE FINISHED')


@measure
def gather_and_backup_explorers():
    logging.info('STARTED background job: EXPLORERS UPDATE')
    with open('backup_explorers.json') as explorers_urls:
        explorerz = json.load(explorers_urls)
    
    updated_urls = electrum_lib.call_explorers_and_update_status(explorerz)

    with open('backup_explorers.json', 'w') as f:
        json.dump(updated_urls, f, indent=4)
        logging.info('background job: EXPLORERS UPDATE FINISHED')




#### AWS S3 UPLOAD BACKGROUND JOBS

def backup_electrums_data_to_aws():
    logging.info('STARTED background job: UPLOAD ELECTRUMS data to AWS')
    file_name = 'backup_electrums.json'
    bucket = 'rocky-cove-80142'
    object_name = 'backup_electrums.json'

    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        logging.info(response)
    except ClientError as e:
        logging.error(e)
        logging.error('AWS-S3 ELECTRUMS UPLOAD: FAILURE')
        return False
    logging.info('AWS-S3 ELECTRUMS UPLOAD: SUCCESS')
    return True

def backup_explorers_data_to_aws():
    logging.info('STARTED background job: UPLOAD EXPLORERS data to AWS')
    file_name = 'backup_explorers.json'
    bucket = 'rocky-cove-80142'
    object_name = 'backup_explorers.json'

    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        logging.info(response)
    except ClientError as e:
        logging.error(e)
        logging.error('AWS-S3 EXPLORERS UPLOAD: FAILURE')
        return False
    logging.info('AWS-S3 EXPLORERS UPLOAD: SUCCESS')
    return True


scheduler = BackgroundScheduler()
scheduler.add_job(func=gather_and_backup_electrums, trigger="interval", seconds=60)
scheduler.add_job(func=gather_and_backup_explorers, trigger="interval", seconds=100)
scheduler.add_job(func=backup_electrums_data_to_aws, trigger="interval", minutes=30)
scheduler.add_job(func=backup_explorers_data_to_aws, trigger="interval", minutes=30)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ['PORT'])


### Error handling

#@app.errorhandler(500)
#def rollback_electrums():
#    logging
#    restore_electrums_from_aws()