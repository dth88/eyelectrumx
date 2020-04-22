import datetime
import json
import requests
import atexit
from lib import electrum_lib
from lib import electrums

from flask import Flask, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)


electrum_urls = {}
explorers_urls = {}


@app.before_first_request
def get_electrum_urls():
    global electrum_urls
    electrum_urls = electrum_lib.restore_electrums_from_backup()
    global explorers_urls
    explorers_urls = electrum_lib.restore_explorers_from_backup()



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
    global explorers_urls
    return render_template('explorers.html', explorers_urls=explorers_urls)


@app.route("/api")
def api():
    return render_template('api-docs.html')


@app.errorhandler(404)
def page_not_found(e):
    return 'woops, page with this url does not exist', 404



### API CALLS

@app.route('/api/electrums')
def get_all_electrums():
    global electrum_urls
    return jsonify(electrum_urls)


@app.route('/api/atomicdex-mob')
def get_only_atomicdex_mobile_electrums():
    global electrum_urls
    d = {}
    for coin, urls in electrum_urls.items():
        if coin in electrums.atomic_dex_mobile:
            d[coin] = urls
    return jsonify(d)


@app.route('/api/explorers')
def get_all_explorers():
    global explorers_urls
    return jsonify(explorers_urls)


#scheduler = BackgroundScheduler()
#scheduler.add_job(func=mine_one_block_first_node, trigger="interval", seconds=2)
#if estimatesmartfee:
#    scheduler.add_job(func=combined_send, trigger="interval", seconds=1)

#scheduler.start()



#atexit.register(lambda: scheduler.shutdown())


if __name__ == "__main__":
    app.run(host="localhost", port="8080")