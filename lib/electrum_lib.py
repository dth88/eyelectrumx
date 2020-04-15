import ssl
import json
import socket
import requests
from functools import wraps
from time import time
from requests.exceptions import RequestException
from time import sleep
from electrum_list import electrum_links




def measure(func):
    @wraps(func)
    def _time_it(*args, **kwargs):
        start = int(round(time() * 1000))
        try:
            return func(*args, **kwargs)
        finally:
            end_ = int(round(time() * 1000)) - start
            print(f"Total execution time: {end_ if end_ > 0 else 0} ms")
    return _time_it


@measure
def gather_tcp_electrumx_links_into_dict(electrum_links):
    output = {}
    counter = 0
    for k,v in electrum_links.items():
        r = requests.get(v).json()
        urls = []
        if 'rpc_nodes' in r:
            for url in r['rpc_nodes']:
                urls.append(url)
                counter += 1
        else:
            for url in r:
                try:
                    if 'SSL' in url['protocol']:
                        continue
                    elif 'TCP' in url['protocol']:
                        urls.append(url)
                        counter += 1
                except KeyError:
                    urls.append(url)
                    counter += 1
                except TypeError:
                    urls.append(url)
                    counter += 1
        output[k] = urls
    return output, counter


def tcp_call_electrumx(url, port, content):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    s.connect((url, port))
    s.sendall(json.dumps(content).encode('utf-8')+b'\n')
    sleep(0.1)
    s.shutdown(socket.SHUT_WR)
    response = ''
    while True:
        data = s.recv(1024)
        if (not data):
            break
        response += data.decode()
    s.close()
    return response


def http_call_electrumx(url, content):
    response = requests.post(url, json=content).json()
    return response


# TODO: figure out ssl...
def tcp_call_electrumx_ssl(url, port, content):
    context = ssl.create_default_context()
    response = ''
    with socket.create_connection((url, port)) as sock:
        with context.wrap_socket(sock, server_hostname=url) as ssock:
            ssock.sendall(json.dumps(content).encode('utf-8')+b'\n')
            while True:
                data = ssock.recv(1024)
                if (not data):
                    break
                response += data.decode()
    return response


def pretty_print(electrum_urls):
    for coin,urls in electrum_urls.items():
        print(coin)
        for url in urls:
            try:
                print('{} --> {} --> {}'.format(url['url'], url['current_status'], url['contact']))
            except KeyError:
                print('{} --> {}'.format(url['url'], url['current_status']))
        print()


@measure
def call_electrums_and_update_status(electrum_urls, electrum_call, eth_call):
    for coin, urls in electrum_urls.items():
        for url in urls:
            try:
                electrum, port = url['url'].split(':')
                try:
                    r = tcp_call_electrumx(electrum, int(port), electrum_call)
                    #if electrum is reachable
                    try:
                        #update if status exists
                        if url['current_status']:
                            url['current_status']['alive'] = True
                            #qtum has different response from other electrums for some reason...
                            if 'QTUM' in coin:
                                url['current_status']['version'] = r.split()[5][:-2]
                            else:
                                url['current_status']['version'] = r.split()[4][:-2]
                            url['current_status']['downtime'] = 0
                            url['current_status']['uptime'] = time() if not url['current_status']['uptime'] else url['current_status']['uptime']
                    except KeyError:
                        #creation for the first time
                        url['current_status'] = {}
                        url['current_status']['alive'] = True
                        if 'QTUM' in coin:
                            url['current_status']['version'] = r.split()[5][:-2]
                        else:
                            url['current_status']['version'] = r.split()[4][:-2]
                        url['current_status']['uptime'] = time()
                        url['current_status']['downtime'] = 0
                except socket.error:
                    #if electrum is unreachable
                    try:
                        #update if status exists
                        if url['current_status']:
                            url['current_status']['alive'] = False
                            url['current_status']['uptime'] = 0
                            url['current_status']['downtime'] = time() if not url['current_status']['downtime'] else url['current_status']['downtime']
                    except KeyError:
                        #first time creation for unreachable electrum
                        url['current_status'] = {}
                        url['current_status']['alive'] = False
                        url['current_status']['uptime'] = 0
                        url['current_status']['downtime'] = time()
            #if url['url'].split(':') has more than 2 members then
            #value error is raised because of http://url:port
            #then url just needs regular http requests call
            #in our case these urls belong only to eth parity nodes
            except ValueError:
                try:
                    r = http_call_electrumx(url['url'], eth_call)
                    #if parity node is reachable
                    try:
                        #update if status exists
                        if url['current_status']:
                            url['current_status']['alive'] = True
                            url['current_status']['uptime'] = time() if not url['current_status']['uptime'] else url['current_status']['uptime']
                            url['current_status']['downtime'] = 0
                    except KeyError:
                        #creation for the first time
                        url['current_status'] = {}
                        url['current_status']['alive'] = True
                        url['current_status']['uptime'] = time()
                        url['current_status']['downtime'] = 0
                except RequestException:
                    # if parity node is unreachable
                    try:
                        #update if status exists
                        if url['current_status']:
                            url['current_status']['alive'] = False
                            url['current_status']['uptime'] = 0
                            url['current_status']['downtime'] = time() if not url['current_status']['downtime'] else url['current_status']['downtime']
                    except KeyError:
                        #first time creation for unreachable parity node
                        url['current_status'] = {}
                        url['current_status']['alive'] = False
                        url['current_status']['uptime'] = 0
                        url['current_status']['downtime'] = time()
    return electrum_urls


def backup(electrum_urls):
    with open('data/backup.json', 'w') as f:
        json.dump(electrum_urls, f)


def restore_from_backup():
    backup = {}
    with open('data/backup.json', 'r') as f:
        backup = json.load(f)
    return backup




if __name__ == "__main__":
    version_call = {
        "jsonrpc" : "2.0",
        "method": "server.version",
        "params": [],
        "id": 0
    }

    eth_call = {
        "jsonrpc" : "2.0",
        "method": "web3_clientVersion",
        "params": [],
        "id": 0
    }


    ping_call = {
        "jsonrpc" : "2.0",
        "method": "server.ping",
        "params": [],
        "id": 0
    }

    #result = http_call_electrumx('http://195.201.0.6:8555', eth_call)
    #print(result, end='')

    #d, c = gather_tcp_electrumx_links_into_dict(electrum_links)
    d = restore_from_backup()
    d = call_electrums_and_update_status(d, version_call, eth_call)
    backup(d)
    pretty_print(d)