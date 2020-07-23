import os
import sys
import json
import boto3
import atexit
import logging
import requests
import threading

from lib import electrums
from lib import electrum_lib

from functools import wraps
from time import time, sleep
from json import JSONDecodeError
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from flask import Flask, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler


class FlaskApp(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskApp, self).__init__(*args, **kwargs)
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        self._activate_on_startup()

    def _activate_on_startup(self):
        def restore_data_from_aws():
            logging.info('_activate_on_startup execution started')
            #restore_electrums
            file_name = 'backup_electrums.json'
            bucket = 'rocky-cove-80142'
            object_name = 'backup_electrums.json'
            s3_client = boto3.client('s3')
            try:
                s3_client.download_file(bucket, object_name, file_name)
            except ClientError as e:
                logging.error(e)
                logging.error('AWS-S3 electrums DOWNLOAD: FAILURE')
            logging.info('AWS-S3 electrums DOWNLOAD: SUCCESS')
            #restore_explorers
            file_name = 'backup_explorers.json'
            bucket = 'rocky-cove-80142'
            object_name = 'backup_explorers.json'
            try:
                s3_client.download_file(bucket, object_name, file_name)
            except ClientError as e:
                logging.error(e)
                logging.error('AWS-S3 explorers DOWNLOAD: FAILURE')
            logging.info('AWS-S3 explorers DOWNLOAD: SUCCESS')

            logging.info('creating local backups of json data')
            try:
                with open('backup_electrums.json') as electrum_urls:
                    electrumz = json.load(electrum_urls)
                logging.info('backup_electrums json from aws is valid, creating local backup...')
                with open('local_backup_electrums.json', 'w') as f:
                    json.dump(electrumz, f)
                logging.info('local_backup_electrums - CREATED')
            except JSONDecodeError as e:
                logging.error(e)
                logging.error("ELECTRUMS JSON DATA FROM AWS IS INVALID!!!")
            
            try:
                with open('backup_explorers.json') as explorers_urls:
                    explorerz = json.load(explorers_urls)
                logging.info('backup_explorers json from aws is valid, creating local backup...')
                with open('local_backup_explorers.json', 'w') as f:
                    json.dump(explorerz, f)
                logging.info('local_backup_explorers - CREATED')
            except JSONDecodeError as e:
                logging.error(e)
                logging.error("EXPLORERS JSON DATA FROM AWS IS INVALID!!!")
            
            logging.info('time preparation....')
            global last_ping_electrumz
            last_ping_electrumz = datetime.now()
            global last_ping_explorers
            last_ping_explorers = datetime.now()
            logging.info('time preparation done')

            logging.info('_activate_on_startup execution finished')
        
        t1 = threading.Thread(target=restore_data_from_aws)
        t1.start()


app = FlaskApp(__name__)
    
#logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logging.getLogger('apscheduler').setLevel(logging.DEBUG)


## TODO: create additional json files for adex-mob and adex-pro
## so it would not lock main electrum json with many requests.


### TEMPLATES
@app.route("/")
def main():
    global last_ping_electrumz
    secs_since_last_ping = datetime.now() - last_ping_electrumz
    secs_since_last_ping = "{}".format(secs_since_last_ping.seconds)
    try:
        with open('backup_electrums.json') as electrum_urls:
            electrumz = json.load(electrum_urls)
        return render_template('index.html', urlz=electrumz, last_ping=secs_since_last_ping)
    except JSONDecodeError as e:
        logging.error(e)
        logging.error("there's decode error RESTORING FROM LOCAL backup")
        with open('local_backup_electrums.json') as electrum_urls:
            electrumz = json.load(electrum_urls)
        return render_template('index.html', urlz=electrumz, last_ping=secs_since_last_ping)


@app.route("/adex-mob")
def filter_mob():
    global last_ping_electrumz
    secs_since_last_ping = datetime.now() - last_ping_electrumz
    secs_since_last_ping = "{}".format(secs_since_last_ping.seconds)
    try:
        with open('backup_electrums.json') as electrum_urls:
            electrumz = json.load(electrum_urls)
        return render_template('adex-mob.html', urlz=electrumz, adexmob=electrums.adex_mob, last_ping=secs_since_last_ping)
    except JSONDecodeError as e:
        logging.error(e)
        logging.error("there's decode error RESTORING FROM LOCAL backup")
        with open('local_backup_electrums.json') as electrum_urls:
            electrumz = json.load(electrum_urls)
        return render_template('index.html', urlz=electrumz, adexmob=electrums.adex_mob, last_ping=secs_since_last_ping)


@app.route("/adex-pro")
def filter_pro():
    global last_ping_electrumz
    secs_since_last_ping = datetime.now() - last_ping_electrumz
    secs_since_last_ping = "{}".format(secs_since_last_ping.seconds)
    try:
        with open('backup_electrums.json') as electrum_urls:
            electrumz = json.load(electrum_urls)
        return render_template('adex-pro.html', urlz=electrumz, adexpro=electrums.adex_pro, last_ping=secs_since_last_ping)
    except JSONDecodeError as e:
        logging.error(e)
        logging.error("there's decode error RESTORING FROM LOCAL backup")
        with open('local_backup_electrums.json') as electrum_urls:
            electrumz = json.load(electrum_urls)
        return render_template('index.html', urlz=electrumz, adexpro=electrums.adex_pro, last_ping=secs_since_last_ping)


@app.route("/explorers")
def explorers():
    global last_ping_explorers
    secs_since_last_ping = datetime.now() - last_ping_explorers
    secs_since_last_ping = "{}".format(secs_since_last_ping.seconds)
    try:
        with open('backup_explorers.json') as explorers_urls:
            explorerz = json.load(explorers_urls)
        return render_template('explorers.html', urlz=explorerz, last_ping=secs_since_last_ping)
    except JSONDecodeError as e:
        logging.error(e)
        logging.error("there's decode error in EXPLORERS - RESTORING FROM LOCAL backup")
        with open('local_backup_explorers.json') as explorers_urls:
            explorerz = json.load(explorers_urls)
        return render_template('explorers.html', urlz=explorerz, last_ping=secs_since_last_ping)


@app.route("/api")
def api():
    return render_template('api-docs.html')



### ENDPOINTS

@app.route('/api/electrums')
def get_all_electrums():
    try:
        with open('backup_electrums.json') as electrum_urls:
            electrumz = json.load(electrum_urls)
        return jsonify(electrumz)
    except JSONDecodeError as e:
        logging.error(e)
        logging.error("there's decode error RESTORING FROM LOCAL backup")
        with open('local_backup_electrums.json') as electrum_urls:
            electrumz = json.load(electrum_urls)
        return jsonify(electrumz)


@app.route('/api/adex-mob')
def get_adex_mob_electrums():
    d = {}
    try:
        with open('backup_electrums.json') as electrum_urls:
            electrumz = json.load(electrum_urls)
            for coin, urls in electrumz.items():
                if coin in electrums.adex_mob:
                    urls_without_ssl = []
                    for url in urls:
                        if url['protocol'] == 'TCP':
                            urls_without_ssl.append(url)
                    d[coin] = urls_without_ssl
            return jsonify(d)
    except JSONDecodeError as e:
        logging.error(e)
        logging.error("there's decode error RESTORING FROM LOCAL backup")
        with open('local_backup_electrums.json') as electrum_urls:
            electrumz = json.load(electrum_urls)
            for coin, urls in electrumz.items():
                if coin in electrums.adex_mob:
                    urls_without_ssl = []
                    for url in urls:
                        if url['protocol'] == 'TCP':
                            urls_without_ssl.append(url)
                    d[coin] = urls_without_ssl
    return jsonify(d)


@app.route('/api/adex-pro')
def get_adex_pro_electrums():
    try:
        with open('backup_electrums.json') as electrum_urls:
            electrumz = json.load(electrum_urls)
            d = {}
            for coin, urls in electrumz.items():
                if coin in electrums.adex_pro:
                    urls_without_ssl = []
                    for url in urls:
                        if url['protocol'] == 'TCP':
                            urls_without_ssl.append(url)
                    d[coin] = urls_without_ssl
            return jsonify(d)
    except JSONDecodeError as e:
        logging.error(e)
        logging.error("there's decode error RESTORING FROM LOCAL backup")
        with open('local_backup_electrums.json') as electrum_urls:
            electrumz = json.load(electrum_urls)
            d = {}
            for coin, urls in electrumz.items():
                if coin in electrums.adex_pro:
                    urls_without_ssl = []
                    for url in urls:
                        if url['protocol'] == 'TCP':
                            urls_without_ssl.append(url)
                    d[coin] = urls_without_ssl
            return jsonify(d)


@app.route('/api/explorers')
def get_all_explorers():
    try:
        with open('backup_explorers.json') as explorers_urls:
            explorerz = json.load(explorers_urls)
            return jsonify(explorerz)
    except JSONDecodeError as e:
        logging.error(e)
        logging.error("there's decode error in EXPLORERS - RESTORING FROM LOCAL backup")
        with open('local_backup_explorers.json') as explorers_urls:
            explorerz = json.load(explorers_urls)
        return jsonify(explorerz)



#DEBUG

@app.route('/debug/electrums')
def get_debug_electrums():
    with open('backup_electrums.json') as explorers_urls:
        explorerz = explorers_urls.read()
        return render_template('debug.html', urlz=explorerz)


@app.route('/debug/local_electrums')
def get_debug_local_electrums():
    with open('local_backup_electrums.json') as explorers_urls:
        explorerz = explorers_urls.read()
        return render_template('debug.html', urlz=explorerz)



### Error handling
#@app.errorhandler(500)
#def rollback_electrums():
#    logging.error("500 again! Rolling back from AWS")
#    restore_electrums_from_aws()



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
    global last_ping_electrumz
    last_ping_electrumz = datetime.now()

    logging.info('STARTED background job: ELECTRUMS UPDATE')
    try:
        with open('backup_electrums.json') as electrum_urls:
            electrumz = json.load(electrum_urls)
        #make local backup if json is loadable
        with open('local_backup_electrums.json', 'w') as f:
            json.dump(electrumz, f)
    # There's an AUTOMAGICAL bug here which happens randomly that I cant get my head around. 
    # It is concatenating one additional curly brace at the end of 'backup_electrums.json'
    # and making it unable to load as json file(raise JSONDecodeError("Extra data", s, end)
    # app[web.1]: json.decoder.JSONDecodeError: Extra data: line 2578 column 2 (char 74668)
    # i was able to fix it only with removing this last curly brace basically "by hands" 
    # if Internal Server Error 500 happens, it is most likely because of this bug.
    # The "funniest" thing that it only happens in HEROKU environment, cant reproduce anywhere else...
    #
    # So... another case came in json.decoder.JSONDecodeError:
    # Invalid control character at: line 2267 column 57 (char 65576)
    # where somehow this --> ("email": "0x03-ctrlc(at)protonmail.com",) turned into this entry ---> 
    # ("email": "0x03-ctrlc(at)protonmail.com,,)
    # seems like i need a real db for all that...
    except JSONDecodeError as e:
        logging.error(e)
        #if there's decode error restore from local backup
        with open('local_backup_electrums.json') as electrum_urls:
            electrumz = json.load(electrum_urls)

    updated_urls = electrum_lib.call_electrums_and_update_status(electrumz, electrums.electrum_version_call, electrums.eth_call)

    with open('backup_electrums.json', 'w') as f:
        json.dump(updated_urls, f)
    logging.info('background job: ELECTRUMS UPDATE FINISHED')


@measure
def gather_and_backup_explorers():
    global last_ping_explorers
    last_ping_explorers = datetime.now()

    logging.info('STARTED background job: EXPLORERS UPDATE')
    try:
        with open('backup_explorers.json') as explorers_urls:
            explorerz = json.load(explorers_urls)
        #make local backup if json is loadable
        with open('local_backup_explorers.json', 'w') as f:
            json.dump(explorerz, f)
    except JSONDecodeError as e:
        logging.error(e)
        #if there's decode error restore from local backup
        with open('local_backup_explorers.json') as explorers_urls:
            explorerz = json.load(explorers_urls)

    updated_urls = electrum_lib.call_explorers_and_update_status(explorerz)

    with open('backup_explorers.json', 'w') as f:
        json.dump(updated_urls, f)
        logging.info('background job: EXPLORERS UPDATE FINISHED')



#### AWS S3 UPLOAD BACKGROUND JOBS

def backup_electrums_data_to_aws():
    logging.info('STARTED background job: UPLOAD ELECTRUMS data to AWS')
    file_name = 'local_backup_electrums.json'
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
    file_name = 'local_backup_explorers.json'
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
scheduler.add_job(func=gather_and_backup_electrums, trigger="interval", seconds=200)
scheduler.add_job(func=gather_and_backup_explorers, trigger="interval", seconds=111)
scheduler.add_job(func=backup_electrums_data_to_aws, trigger="interval", minutes=60)
scheduler.add_job(func=backup_explorers_data_to_aws, trigger="interval", minutes=60)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ['PORT'])