import ssl
import json
import socket
import requests
from functools import wraps
from time import time, sleep
from datetime import datetime
from requests.exceptions import RequestException

from electrums import (all_tickers, link, atomic_dex_mobile,
                       electrum_version_call, eth_call, eth_link)



def stop_email_parsing(electrum_urls):
    for coin, urls in electrum_urls.items():
        for url in urls:
            email = url['contact'].get('email')
            if email:
                left, right = email.split('@')
                url['contact']['email'] = '{}(at){}'.format(left, right)
    return electrum_urls


def get_explorers_json_data():
    explorers_json = {}
    with open('data/explorers.json', 'r') as f:
        explorers_json = json.load(f)
    return explorers_json


def save_explorers_links_to_local_dict(explorers_json):
    new_dict = {}
    for ticker in explorers_json:
        new_dict[ticker['abbr']] = ticker['explorerUrl']
    return new_dict


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


def combine_electrums_repo_links(all_tickers, link, eth_link):
    repo_links = {}
    for ticker in all_tickers:
        if 'ETH' in ticker:
            repo_links[ticker] = '{}{}'.format(eth_link, ticker)
        else:
            repo_links[ticker] = '{}{}'.format(link, ticker)
    return repo_links



def gather_tcp_electrumx_links_into_dict(electrum_links):
    output = {}
    counter = 0
    for coin, link in electrum_links.items():
        try:
            r = requests.get(link).json()
        except Exception as e:
            print(e)
        urls = []
        if 'rpc_nodes' in r:
            for url in r['rpc_nodes']:
                urls.append(url)
                counter += 1
        else:
            for url in r:
                new_contacts = {}
                try:
                    if 'SSL' in url['protocol']:
                        continue
                except KeyError:
                    pass
                try:
                    for contact in url['contact']:
                        email = contact.get('email')
                        discord = contact.get('discord')
                        github = contact.get('github')
                        if email:
                            new_contacts['email'] = email
                        if discord:
                            new_contacts['discord'] = discord
                        if github:
                            new_contacts['github'] = github
                    url['contact'] = new_contacts
                    urls.append(url)
                    counter += 1
                except KeyError:
                    url['contact'] = {}
                    urls.append(url)
        output[coin] = urls
    output = stop_email_parsing(output)
    return output, counter


def http_call_explorer(url):
    response = requests.get(url)
    return response



def call_explorers_and_update_status_new(explorers_urls):
    output = {}
    for coin, urls in explorers_urls.items():
        updated_urls = []
        for url in urls:
            new_url = {'url': url}
            try:
                _ = http_call_explorer(url)
                try:
                    #update if status exists
                    if new_url['current_status']:
                        new_url['current_status']['alive'] = True
                        new_url['current_status']['downtime'] = 0
                        new_url['current_status']['uptime'] = datetime.now().strftime("%b-%d %H:%M") if not url['current_status']['uptime'] else url['current_status']['uptime']
                except KeyError:
                    #create if there's no status dict
                    new_url['current_status'] = {}
                    new_url['current_status']['alive'] = True
                    new_url['current_status']['uptime'] = datetime.now().strftime("%b-%d %H:%M")
                    new_url['current_status']['downtime'] = 0
            #if explorer is unreachable
            except RequestException:
                try:
                    #update if status exists
                    if new_url['current_status']:
                        new_url['current_status']['alive'] = False
                        new_url['current_status']['uptime'] = 0
                        new_url['current_status']['downtime'] = datetime.now().strftime("%b-%d %H:%M") if not url['current_status']['downtime'] else url['current_status']['downtime']
                except KeyError:
                    #create if there's no status dict
                    new_url['current_status'] = {}
                    new_url['current_status']['alive'] = False
                    new_url['current_status']['uptime'] = 0
                    new_url['current_status']['downtime'] = datetime.now().strftime("%b-%d %H:%M")
            updated_urls.append(new_url)
        output[coin] = updated_urls
    return output



def call_explorers_and_update_status(explorers_urls):
    for coin, urls in explorers_urls.items():
        for url in urls:
            try:
                _ = http_call_explorer(url['url'])
                try:
                    #update if status exists
                    if url['current_status']:
                        url['current_status']['alive'] = True
                        url['current_status']['downtime'] = 0
                        url['current_status']['uptime'] = datetime.now().strftime("%b-%d %H:%M") if not url['current_status']['uptime'] else url['current_status']['uptime']
                except KeyError:
                    #create if there's no status dict
                    url['current_status'] = {}
                    url['current_status']['alive'] = True
                    url['current_status']['uptime'] = datetime.now().strftime("%b-%d %H:%M")
                    url['current_status']['downtime'] = 0
            #if explorer is unreachable
            except RequestException:
                try:
                    #update if status exists
                    if url['current_status']:
                        url['current_status']['alive'] = False
                        url['current_status']['uptime'] = 0
                        url['current_status']['downtime'] = datetime.now().strftime("%b-%d %H:%M") if not url['current_status']['downtime'] else url['current_status']['downtime']
                except KeyError:
                    #create if there's no status dict
                    url['current_status'] = {}
                    url['current_status']['alive'] = False
                    url['current_status']['uptime'] = 0
                    url['current_status']['downtime'] = datetime.now().strftime("%b-%d %H:%M")
    return explorers_urls


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


def call_electrums_and_update_status(electrum_urls, electrum_call, eth_call):
    for coin, urls in electrum_urls.items():
        for url in urls:
            #if url['url'].split(':') has exactly 2 members 
            #then we create a simple tcp call with socket
            try:
                electrum, port = url['url'].split(':')
                #if electrum is reachable
                try:
                    r = tcp_call_electrumx(electrum, int(port), electrum_call)
                    try:
                        #update if status exists
                        if url['current_status']:
                            url['current_status']['alive'] = True
                            #qtum has different response from other electrums for some reason...
                            if 'QTUM' in coin:
                                url['current_status']['version'] = r.split()[5][:-2]
                            else:
                                #strange index error... trying to debug...
                                try:
                                    url['current_status']['version'] = r.split()[4][:-2]
                                except IndexError:
                                    print("EXCEPTION!!!11  Index Error!")
                                    print('url: {}, response: {}'.format(url, r))
                            url['current_status']['downtime'] = 0
                            url['current_status']['uptime'] = datetime.now().strftime("%b-%d %H:%M") if not url['current_status']['uptime'] else url['current_status']['uptime']
                    except KeyError:
                        #create if there's no status dict
                        url['current_status'] = {}
                        url['current_status']['alive'] = True
                        if 'QTUM' in coin:
                            url['current_status']['version'] = r.split()[5][:-2]
                        else:
                            #strange index error... trying to debug...
                            try:
                                url['current_status']['version'] = r.split()[4][:-2]
                            except IndexError:
                                print("EXCEPTION!!!11  Index Error!")
                                print('url: {}, response: {}'.format(url, r))
                        url['current_status']['uptime'] = datetime.now().strftime("%b-%d %H:%M")
                        url['current_status']['downtime'] = 0
                #if electrum is unreachable
                except socket.error:
                    try:
                        #update if status exists
                        if url['current_status']:
                            url['current_status']['alive'] = False
                            url['current_status']['uptime'] = 0
                            url['current_status']['downtime'] = datetime.now().strftime("%b-%d %H:%M") if not url['current_status']['downtime'] else url['current_status']['downtime']
                    except KeyError:
                        #create if there's no status dict
                        url['current_status'] = {}
                        url['current_status']['alive'] = False
                        url['current_status']['uptime'] = 0
                        url['current_status']['downtime'] = datetime.now().strftime("%b-%d %H:%M")
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
                            url['current_status']['uptime'] = datetime.now().strftime("%b-%d %H:%M") if not url['current_status']['uptime'] else url['current_status']['uptime']
                            url['current_status']['downtime'] = 0
                    except KeyError:
                        #creation for the first time
                        url['current_status'] = {}
                        url['current_status']['alive'] = True
                        url['current_status']['uptime'] = datetime.now().strftime("%b-%d %H:%M")
                        url['current_status']['downtime'] = 0
                except RequestException:
                    # if parity node is unreachable
                    try:
                        #update if status exists
                        if url['current_status']:
                            url['current_status']['alive'] = False
                            url['current_status']['uptime'] = 0
                            url['current_status']['downtime'] = datetime.now().strftime("%b-%d %H:%M") if not url['current_status']['downtime'] else url['current_status']['downtime']
                    except KeyError:
                        #first time creation for unreachable parity node
                        url['current_status'] = {}
                        url['current_status']['alive'] = False
                        url['current_status']['uptime'] = 0
                        url['current_status']['downtime'] = datetime.now().strftime("%b-%d %H:%M")
    return electrum_urls



#utilities

def backup_electrums(electrum_urls):
    with open('lib/data/backup_electrums.json', 'w') as f:
        json.dump(electrum_urls, f, indent=4, default=str)


def backup_explorers(explorers_urls):
    with open('lib/data/backup_explorers.json', 'w') as f:
        json.dump(explorers_urls, f, indent=4, default=str)


def backup_electrums_links(links):
    with open('lib/data/backup_electrum_links.json', 'w') as f:
        json.dump(links, f, indent=4, default=str)


def restore_electrums_links():
    backup = {}
    with open('lib/data/backup_electrum_links.json', 'r') as f:
        backup = json.load(f)
    return backup


def restore_explorers_from_backup():
    backup = {}
    with open('lib/data/backup_explorers.json', 'r') as f:
        backup = json.load(f)
    return backup


def restore_electrums_from_backup():
    backup = {}
    with open('lib/data/backup_electrums.json', 'r') as f:
        backup = json.load(f)
    return backup


def pretty_print(electrum_urls):
    for coin,urls in electrum_urls.items():
        print(coin)
        for url in urls:
            try:
                print('{} --> {} --> {}'.format(url['url'], url['current_status'], url['contact']))
            except KeyError:
                print('{} --> {}'.format(url['url'], url['current_status']))
        print()



#if __name__ == "__main__":
    #result = tcp_call_electrumx('electrum2.cipig.net', 10054, version_call)
    #print(result, end='')

    
    #backup_electrums_links(d)

    #repo_links = combine_electrums_repo_links(all_tickers, link, eth_link)
    #exp_json = get_explorers_json_data()
    #exp_local_links = save_explorers_links_to_local_dict(exp_json)
    #exp_local_links = restore_explorers_from_backup()

    #d, c = gather_tcp_electrumx_links_into_dict(repo_links)
    #d = restore_electrums_from_backup()

    #d = call_electrums_and_update_status(d, electrum_version_call, eth_call)
    #backup_electrums(d)

    #de = call_explorers_and_update_status(exp_local_links)
    #backup_explorers(de)
    #pretty_print(d)