## TODO: create parser for komodoplatform/coins repo to automatically 
#  update-rebuild app on coin/electrum/explorer change:
#  1) all_tickers
#  2) adex_mob tickers
#  3) adex_pro tickers
#  4) explorers urls


all_tickers = ["AXE",      "BCH",    "BET",  "BOTS",  "BTC",    "BTCH",  "BTG",      "CCL",   "CHIPS",
               "COQUI",    "CRYPTO", "D",    "DASH",  "DEX",    "DGB",   "DOGE",     "ECA",   "EMC2",
               "FIRO",     "FTC",    "GIN",  "GLEEC", "GRS",    "HODL",  "ILN",      "JUMBLR",
               "KMD",      "KOIN",   "LABS", "LTC",   "MCL",    "MGW",   "MONA",     "MORTY",
               "MSHARK",   "NAV",    "NINJA", "NMC",    "OOT",   "PANGEA",   "PGT",   "PTX",
               "QTUM",     "REVS",   "RICK",  "RVN",    "SMART", "SPACE", "SUPERNET", "THC",   "UFO",
               "VRSC",     "VTC",    "WLC",   "ZEC",   "ZER",    "ZILLA", "tBTC", "tQTUM", "ETH"]


#official electrums/parity-node repo links
link     = "https://raw.githubusercontent.com/KomodoPlatform/coins/master/electrums/"
eth_link = "https://raw.githubusercontent.com/KomodoPlatform/coins/master/ethereum/"


#filters
adex_mob = ["KMD",    "BTC",    "AXE",    "BCH",   "DASH",    "DGB",       "DOGE", 
            "ECA",    "THC",    "PBC",    "FTC",   "FIRO",    "LTC",       "NAV",
            "QTUM",   "RVN",    "VRSC",   "ZEC",   "ZER",     "tBTC",      "GLEEC",
            "ZILLA",  "DEX",    "LABS",   "KOIN",  "MCL",     "SUPERNET", 
            "OOT",    "MORTY",  "RICK",   "ETH"]
                     

adex_pro = ["AXE",    "BET",    "BTC",      "tBTC",    "BCH",      "BTCH",   "BOTS",
            "ZILLA",  "CHIPS",  "CCL",      "COQUI",   "CRYPTO",   "DASH",   "DEX",
            "DGB",    "DOGE",   "EMC2",     "ECA",     "ETH",      "FTC",    "FIRO",
            "GLEEC",  "THC",    "HODL",     "ILN",     "JUMBLR",   "KOIN",   "KMD",
            "LABS",   "LTC",    "MCL",      "MGW",     "MSHARK",   "MONA",   "MORTY",
            "NMC",    "NAV",    "PANGEA",   "PBC",     "QTUM",     "RVN",    "REVS",
            "RICK",   "SPACE",  "SUPERNET", "OOT",     "VRSC",     "WLC",    "ZEC",
            "ZER"]
                              
                               
                          
                        
                                    
                            
                        

                             
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