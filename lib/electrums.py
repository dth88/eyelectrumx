all_tickers = ['AXE', 'AYWA', 'BCH', 'BET', 'BOTS', 'BTC',
               'BTCH', 'BTG', 'CCL', 'CHIPS', 'COQUI', 'CRYPTO',
               'D', 'DASH', 'DEX', 'DGB', 'DOGE', 'ECA', 'EMC2',
               'FJC', 'FTC', 'GAME', 'GIN', 'GRS', 'HODL', 'HODLC',
               'HUSH', 'ILN', 'JUMBLR', 'K64', 'KMD', 'KOIN', 'KV',
               'LABS', 'LTC', 'LUMBER', 'MCL', 'MGW', 'MNX', 'MONA',
               'MORTY', 'MSHARK', 'MUE', 'NAV', 'NINJA', 'OOT',
               'PAC', 'PANGEA', 'PGT', 'PTX', 'QTUM', 'REVS', 'RFOX',
               'RICK', 'RVN', 'SMART', 'SUPERNET', 'THC', 'UFO', 'VRSC',
               'VTC', 'WLC', 'XBC', 'XZC', 'ZEC', 'ZILLA', 'ETH']

#official electrums/parity-node repo links
link = "https://raw.githubusercontent.com/KomodoPlatform/coins/master/electrums/"
eth_link = "https://raw.githubusercontent.com/KomodoPlatform/coins/master/ethereum/"


#filter
atomic_dex_mobile = ["KMD", "BTC", "AWC", "AXE", "BUSD", "BAT",
                     "BCH", "ZILLA", "DAI", "DASH", "DEX", "DGB",
                     "DOGE", "ECA", "ETH", "FTC", "HUSH", "LABS",
                     "LTC", "MORTY", "NAV", "PAX", "QTUM", "RVN",
                     "RFOX", "RICK", "SAI", "SUPERNET", "TUSD",
                     "USDC", "OOT", "VRSC", "VOTE", "ZEC"]


#electrum calls
electrum_version_call = {
    "jsonrpc" : "2.0",
    "method": "server.version",
    "params": [],
    "id": 0
}

electrum_ping_call = {
    "jsonrpc" : "2.0",
    "method": "server.ping",
    "params": [],
    "id": 0
}

#parity node call
eth_call = {
    "jsonrpc" : "2.0",
    "method": "web3_clientVersion",
    "params": [],
    "id": 0
}