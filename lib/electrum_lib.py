import ssl
import json
import socket
import logging
import requests
from functools import wraps
from time import time, sleep
from datetime import datetime
from requests.exceptions import RequestException

from electrums import (all_tickers, link, electrum_version_call, eth_call, eth_link)



def stop_email_parsing(electrum_urls):
    for _, urls in electrum_urls.items():
        for url in urls:
            email = url['contact'].get('email')
            if email:
                left, right = email.split('@')
                url['contact']['email'] = '{}(at){}'.format(left, right)
    return electrum_urls


def get_explorers_json_data():
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
            repo_links[ticker] = "{}{}".format(eth_link, ticker)
        else:
            repo_links[ticker] = "{}{}".format(link, ticker)
    return repo_links


@measure
def gather_electrumx_links_into_dict(electrum_links):
    output = {}
    counter = 0
    for coin, link in electrum_links.items():
        try:
            r = requests.get(link).json()
        except RequestException as e:
            logging.error(e)
        urls = []
        if 'rpc_nodes' in r:
            for url in r['rpc_nodes']:
                try:
                    if url['protocol']:
                        pass
                except KeyError:
                    url['protocol'] = "TCP"
                urls.append(url)
                counter += 1
        else:
            for url in r:
                #debug if json error
                #print('{} --> {}'.format(coin, url))
                new_contacts = {}
                try:
                    if url['protocol']:
                        pass
                except KeyError:
                    url['protocol'] = "TCP"
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


def call_explorers_and_update_status(explorers_urls):
    for _, urls in explorers_urls.items():
        for url in urls:
            try:
                requests.get(url['url'])
                try:
                    #update if status exists
                    if url['current_status']:
                        url['current_status']['alive'] = "true"
                        url['current_status']['downtime'] = "0"
                        url['current_status']['uptime'] = datetime.now().strftime("%b-%d %H:%M") if url['current_status']['uptime'] == "0" else url['current_status']['uptime']
                except KeyError:
                    #create if there's no status dict
                    url['current_status'] = {}
                    url['current_status']['alive'] = "true"
                    url['current_status']['downtime'] = "0"
                    url['current_status']['uptime'] = datetime.now().strftime("%b-%d %H:%M")
            #if explorer is unreachable
            except RequestException:
                try:
                    #update if status exists
                    if url['current_status']:
                        url['current_status']['alive'] = "false"
                        url['current_status']['uptime'] = "0"
                        url['current_status']['downtime'] = datetime.now().strftime("%b-%d %H:%M") if url['current_status']['downtime'] == "0" else url['current_status']['downtime']
                except KeyError:
                    #create if there's no status dict
                    url['current_status'] = {}
                    url['current_status']['alive'] = "false"
                    url['current_status']['uptime'] = "0"
                    url['current_status']['downtime'] = datetime.now().strftime("%b-%d %H:%M")
    return explorers_urls

# this implementation is quite simple and doesn't check cert validity
# in future it might be better to use something like this https://github.com/pbca26/electrum-komodo/blob/master/lib/interface.py#L123
def tcp_call_electrumx_ssl(url, port, content):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.settimeout(2)
  # PROTOCOL_TLS includes all ssl versions even old
  wrappedSocket = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLS, ciphers='ADH-AES256-SHA')
  wrappedSocket.connect((url, port))
  wrappedSocket.sendall(json.dumps(content).encode('utf-8')+b'\n')
  response = b''
  wrappedSocket.settimeout(0.6)
  data = wrappedSocket.recv(1024)
  while data:
      response += data
      try:
          data = wrappedSocket.recv(1024)
          response += data.decode()
      except socket.error:
          break
  wrappedSocket.close()
  return response.decode()


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


@measure
def call_electrums_and_update_status(electrum_urls, electrum_call, eth_call):
    for coin, urls in electrum_urls.items():
        for url in urls:
            #if url['url'].split(':') has exactly 2 members then
            #we do simple tcp call with socket
            try:
                electrum, port = url['url'].split(':')
                #if electrum is reachable
                try:
                    if 'SSL' in url['protocol']:
                      r = tcp_call_electrumx_ssl(electrum, int(port), electrum_call)
                    else:
                      r = tcp_call_electrumx(electrum, int(port), electrum_call)
                    try:
                        #update if status exists
                        if url['current_status']:
                            url['current_status']['alive'] = "true"
                            url['current_status']['downtime'] = "0"
                            url['current_status']['uptime'] = "{}".format(datetime.now().strftime("%b-%d %H:%M")) if url['current_status']['uptime'] == "0" else "{}".format(url['current_status']['uptime'])
                            #qtum has different response from other electrums...
                            try:
                                is_fulcrum = True if 'Fulcrum' in r.split()[0][-7:] else False
                            except IndexError:
                                is_fulcrum = False
                            if 'QTUM' in coin:
                                url['current_status']['version'] = "{}".format(r.split()[5][:-2])
                            elif is_fulcrum:
                                url['current_status']['version'] = "{}({})".format(r.split()[0][-7:], r.split()[1][:5])
                            else:
                                #strange index error... trying to debug...
                                #response: {"id":0,"jsonrpc":"2.0","result":["Fulcrum 1.2.0","1.4"]
                                try:
                                    url['current_status']['version'] = "{}".format(r.split()[4][:-2])
                                except IndexError as e:
                                    logging.error(e)
                                    logging.error('url: {}, response: {}'.format(url, r))
                    except KeyError:
                        #create if there's no status dict
                        url['current_status'] = {}
                        url['current_status']['alive'] = "true"
                        url['current_status']['uptime'] = str(datetime.now().strftime("%b-%d %H:%M"))
                        url['current_status']['downtime'] = "0"
                        url['current_status']['version'] = "Unknown"
                        try:
                            is_fulcrum = True if 'Fulcrum' in r.split()[0][-7:] else False
                        except IndexError:
                            is_fulcrum = False
                        if 'QTUM' in coin:
                            url['current_status']['version'] = "{}".format(r.split()[5][:-2])
                        elif is_fulcrum:
                            url['current_status']['version'] = "{}({})".format(r.split()[0][-7:], r.split()[1][:5])
                        else:
                            #strange index error... trying to debug...
                            try:
                                url['current_status']['version'] = "{}".format(r.split()[4][:-2])
                            except IndexError:
                                logging.debug("EXCEPTION!!!11  Index Error!")
                                logging.debug('url: {}, response: {}'.format(url, r))
                #if electrum is unreachable
                except socket.error:
                    try:
                        #update if status exists
                        if url['current_status']:
                            url['current_status']['alive'] = "false"
                            url['current_status']['uptime'] = "0"
                            url['current_status']['downtime'] = "{}".format(datetime.now().strftime("%b-%d %H:%M")) if url['current_status']['downtime'] == "0" else "{}".format(url['current_status']['downtime'])
                    except KeyError:
                        #create if there's no status dict
                        url['current_status'] = {}
                        url['current_status']['alive'] = "false"
                        url['current_status']['uptime'] = "0"
                        url['current_status']['version'] = "Unknown"
                        url['current_status']['downtime'] = "{}".format(datetime.now().strftime("%b-%d %H:%M"))
            #if url['url'].split(':') has more than 2 members then
            #value error is raised because of http://url:port
            #then url just needs regular http requests call
            #in our case these urls belong only to eth parity nodes
            except ValueError:
                try:
                    r = requests.post(url['url'], json=eth_call).json()
                    #if parity node is reachable
                    try:
                        #update if status exists
                        if url['current_status']:
                            url['current_status']['alive'] = "true"
                            url['current_status']['uptime'] = "{}".format(datetime.now().strftime("%b-%d %H:%M")) if url['current_status']['uptime'] == "0" else "{}".format(url['current_status']['uptime'])
                            url['current_status']['downtime'] = "0"
                    except KeyError:
                        #creation for the first time
                        url['current_status'] = {}
                        url['current_status']['alive'] = "true"
                        url['current_status']['uptime'] = "{}".format(datetime.now().strftime("%b-%d %H:%M"))
                        url['current_status']['downtime'] = "0"
                        url['current_status']['version'] = "Unknown"
                except RequestException:
                    # if parity node is unreachable
                    try:
                        #update if status exists
                        if url['current_status']:
                            url['current_status']['alive'] = "false"
                            url['current_status']['uptime'] = "0"
                            url['current_status']['downtime'] = "{}".format(datetime.now().strftime("%b-%d %H:%M")) if url['current_status']['downtime'] == "0" else url['current_status']['downtime']
                    except KeyError:
                        #first time creation for unreachable parity node
                        url['current_status'] = {}
                        url['current_status']['alive'] = "false"
                        url['current_status']['uptime'] = "0"
                        url['current_status']['downtime'] = "{}".format(datetime.now().strftime("%b-%d %H:%M"))
                        url['current_status']['version'] = "Unknown"
    return electrum_urls



#utilities

def backup_electrums(electrum_urls):
    with open('backup_electrums.json', 'w') as f:
        json.dump(electrum_urls, f)


def backup_explorers(explorers_urls):
    with open('lib/data/backup_explorers.json', 'w') as f:
        json.dump(explorers_urls, f, indent=4, default=str)


def backup_electrums_repo_links(links):
    with open('backup_electrum_repo_links.json', 'w') as f:
        json.dump(links, f, indent=4, default=str)



def backup_electrums_links(links):
    with open('backup_electrum_links.json', 'w') as f:
        json.dump(links, f)


def restore_electrums_links():
    with open('lib/data/backup_electrum_links.json', 'r') as f:
        backup = json.load(f)
    return backup


def restore_explorers_from_backup():
    with open('lib/data/backup_explorers.json', 'r') as f:
        backup = json.load(f)
    return backup


def restore_electrums_from_backup():
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
    # test
    #result = tcp_call_electrumx('electrum2.cipig.net', 10054, version_call)
    #print(result, end='')

    
    #backup_electrums_links(d)
    #exp_json = get_explorers_json_data()
    #exp_local_links = save_explorers_links_to_local_dict(exp_json)
    #exp_local_links = restore_explorers_from_backup()

    #to rebuild electrums json - uncomment this section
    #-----------------
    #repo_links = combine_electrums_repo_links(all_tickers, link, eth_link)
    #print(json.dumps(repo_links, indent=2))
    #backup_electrums_repo_links(repo_links)
    #d, c = gather_electrumx_links_into_dict(repo_links)
    #backup_electrums_links(d)
    #print(json.dumps(d, indent=2))
    #d = call_electrums_and_update_status(d, electrum_version_call, eth_call)
    #backup_electrums(d)
    #pretty_print(d)
    #-----------------

    #d = restore_electrums_from_backup()
    #de = call_explorers_and_update_status(exp_local_links)
    #backup_explorers(de)
    #pretty_print(d)
    #0-date bug
    #"HODLC":[{"contact":{},"current_status":{"alive":"true","downtime":"0","uptime":"Jun-24 17:07","version":"1.14.0"},"url":"hodl2.amit.systems:17989"},
    #         {"contact":{},"current_status":{"alive":"true","downtime":"0","uptime":"0","version":"1.14.0"},"url":"hodl.amit.systems:17989"}],