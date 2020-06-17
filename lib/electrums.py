all_tickers = ['AXE',      'BCH',     'BET',    'BOTS',     'BTC',      'BTCH',  
               'BTG',      'CCL',     'CHIPS',  'COQUI',    'CRYPTO',   'D',        
               'DASH',     'DEX',     'DGB',    'DOGE',     'ECA',      'EMC2',     
               'FTC',      'GAME',    'GIN',    'GRS',      'HODL',     'HODLC',   
               'HUSH',     'ILN',     'JUMBLR', 'KMD',      'KOIN',     'LABS',   
               'LTC',      'LUMBER',  'MCL',    'MGW',      'MONA',     'MORTY',   
               'MUE',      'MSHARK',  'NAV',    'NINJA',    'NMC',      'OOT',
               'PANGEA',   'PGT',     'PTX',    'QTUM',     'REVS',     'RFOX',  
               'RICK',     'RVN',     'SMART',  'SUPERNET', 'THC',      'UFO',
               'VOTE2020', 'VRSC',    'VTC',    'WLC',      'XBC',      'XZC',
               'ZEC',      'ZER',     'ZILLA',  'ETH']

#'AYWA', "AWC", "BAT", "DAI", 'FJC', "VOTE", 'K64', 'KV', 'MNX', "PAX", 'PAC', "TUSD" "BUSD"
#official electrums/parity-node repo links
link = "https://raw.githubusercontent.com/KomodoPlatform/coins/master/electrums/"
eth_link = "https://raw.githubusercontent.com/KomodoPlatform/coins/master/ethereum/"


#filters
atomic_dex_mobile = ['KMD',  'BTC', 'BCH',  'DASH', 'DEX', 'DGB',
                     'LTC',  'ETH',  'USDC',   'MORTY',  'RICK',  
                     'HUSH', 'LABS',  'QTUM', 'RVN',  'ZEC', 
                     'SUPERNET', 'VRSC', 'AXE', 'ZILLA', 'DOGE',
                     'ECA', 'FTC', 'NAV', 'RFOX', 'OOT', 'VOTE2020']
                     

atomic_dex_pro =    ["KMD",  "BTC",  "BCH",  "DASH", "DEX",  "DGB",
                     "LTC", "ETH", "USDC", "MORTY", "RICK", "HUSH",
                     "LABS",  "QTUM",  "RVN",  "ZEC",  "SUPERNET",  
                     "VRSC", "BET", "BOTS", "CRYPTO", "ILN" "JUMBLR", 
                     "MCL", "MGW", "PANGEA", "REVS", "CHIPS"]

                             
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