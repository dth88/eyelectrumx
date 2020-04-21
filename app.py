import datetime
import json
import requests
import atexit
from lib import electrum_lib

from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)

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

#scheduler = BackgroundScheduler()
#scheduler.add_job(func=mine_one_block_first_node, trigger="interval", seconds=2)
#if estimatesmartfee:
#    scheduler.add_job(func=combined_send, trigger="interval", seconds=1)

#scheduler.start()



#atexit.register(lambda: scheduler.shutdown())


if __name__ == "__main__":
    app.run(host="localhost", port="8080")