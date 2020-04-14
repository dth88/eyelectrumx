import ssl
import json
import socket
import requests
from time import sleep
from electrum_list import electrum_links



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
    s.connect((url, port))
    s.sendall(json.dumps(content).encode('utf-8')+b'\n')
    sleep(0.5)
    s.shutdown(socket.SHUT_WR)
    res = ''
    while True:
        data = s.recv(1024)
        if (not data):
            break
        res += data.decode()
    s.close()
    return res


def http_call_electrumx(url, content):
    r = requests.post(url, json=content).json()
    return r


# TODO: figure out ssl...
def tcp_call_electrumx_ssl(url, port, content):
    context = ssl.create_default_context()
    res = ''
    with socket.create_connection((url, port)) as sock:
        with context.wrap_socket(sock, server_hostname=url) as ssock:
            ssock.sendall(json.dumps(content).encode('utf-8')+b'\n')
            while True:
                data = ssock.recv(1024)
                if (not data):
                    break
                res += data.decode()
    return res


if __name__ == "__main__":
    ping_call = {
        "jsonrpc" : "2.0",
        "method": "server.ping",
        "params": [],
        "id": 0
    }

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


    #result = tcp_call_electrumx('electrum1.cipig.net', 10006, version_call)
    #print(result, end='')




    d, c = gather_tcp_electrumx_links_into_dict(electrum_links)
    print(d)
    print(c)