## TODO: create parser for komodoplatform/coins repo to automatically 
#  update-rebuild app on coin/electrum/explorer change:
#  1) all_tickers
#  2) adex_mob tickers
#  3) adex_pro tickers
#  4) explorers urls


all_tickers = ["AXE",      "BCH",    "BET",  "BOTS",  "BTC",    "BTCH",  "BTG",      "CCL",   "CHIPS",
               "COQUI",    "CRYPTO", "D",    "DASH",  "DEX",    "DGB",   "DOGE",     "ECA",   "EMC2",
               "FTC",      "GIN",    "GRS",  "HODL",  "HODLC",  "HUSH",  "ILN",      "JUMBLR",
               "KMD",      "KOIN",   "LABS", "LTC",   "LUMBER", "MCL",   "MGW",      "MONA",  "MORTY",
               "MUE",      "MSHARK", "NAV",  "NINJA", "NMC",    "OOT",   "PANGEA",   "PGT",   "PTX",
               "QTUM",     "REVS",   "RFOX", "RICK",  "RVN",    "SMART", "SUPERNET", "THC",   "UFO",
               "VRSC",     "VTC",    "WLC",  "XBC",   "XZC",    "ZEC",   "ZER",      "ZILLA", "ETH"]


#official electrums/parity-node repo links
link     = "https://raw.githubusercontent.com/KomodoPlatform/coins/master/electrums/"
eth_link = "https://raw.githubusercontent.com/KomodoPlatform/coins/master/ethereum/"


#filters
adex_mob = ["KMD",   "BTC", "AXE",  "BCH",  "DASH", "DGB", "DOGE", "ECA",      "FTC", "LTC",   "NAV",  "QTUM", "RVN", "VRSC", "ZEC",  "XZC", "ZER",  
            "ZILLA", "DEX", "HUSH", "LABS", "KOIN", "MCL", "RFOX", "SUPERNET", "OOT", "MORTY", "RICK",
            "ETH"]
                     

adex_pro = ["KMD", "BTC", "NAV",  "BCH",      "QTUM", "ZEC",    "LTC",  "DASH", "XZC",    "DGB", "CHIPS", "ECA",  "DOGE", "RVN",
            "ILN", "MCL", "REVS", "SUPERNET", "BOTS", "CRYPTO", "VRSC", "HUSH", "PANGEA", "BET", "DEX",   "LABS", "MGW",  "JUMBLR", "MORTY", "RICK",   
            "ETH"]

                             
#electrum call
electrum_version_call = {
    "jsonrpc" : "2.0",
    "method": "server.version",
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