import datetime
import json
import requests
import atexit
from lib import electrum_lib

from flask import Flask, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)


electrum_urls = {}


@app.before_first_request
def get_electrum_urls():
    global electrum_urls 
    electrum_urls = electrum_lib.restore_electrums_from_backup()
    stop_email_parsing()



@app.route("/")
def main():
    global electrum_urls
    return render_template('index.html', electrum_urls=electrum_urls)


@app.route("/atomicdex-mobile")
def filter_mobile():
    global electrum_urls
    return render_template('atomicdex.html', electrum_urls=electrum_urls)


@app.route("/explorers")
def explorers():
    explorers_urls = electrum_lib.restore_explorers_from_backup()
    return render_template('explorers.html', explorers_urls=explorers_urls)


@app.route("/api-docs")
def api():
    return 'api-docs coming...'


@app.errorhandler(404)
def page_not_found(e):
    return 'woops, page with this url does not exist', 404



def stop_email_parsing():
    global electrum_urls
    for k,v in electrum_urls.items():
        for url in v:
            try:
                for k,v in url['contact'].items():
                    if 'email' in k:
                        left, right = v.split('@')
                        v = '{}(at){}'.format(left, right)
            except KeyError:
                pass



#scheduler = BackgroundScheduler()
#scheduler.add_job(func=mine_one_block_first_node, trigger="interval", seconds=2)
#if estimatesmartfee:
#    scheduler.add_job(func=combined_send, trigger="interval", seconds=1)

#scheduler.start()



#atexit.register(lambda: scheduler.shutdown())


if __name__ == "__main__":
    app.run(host="localhost", port="8080")