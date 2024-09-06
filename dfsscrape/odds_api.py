"""
Data source: The Odds API

Example query:
https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/?regions=us&markets=h2h&oddsFormat=american&apiKey=???

python file copied and modified from https://github.com/the-odds-api/samples-python/blob/master/odds.py

The free API key gets 500 requests / month. With 2 markets per request that is 250 calls / month here
"""

import requests
import json
import time
import pathlib

from dfsscrape.config import NFL_SEASON_DATA # path

API_KEY_FILE = pathlib.Path(__file__).parent / '.odds_api_key'
SPORT = 'americanfootball_nfl'
REGIONS = 'us'
MARKETS = 'spreads,totals'
ODDS_FORMAT = 'american'
DATE_FORMAT = 'iso'

class OddsAPIException(Exception):
    pass

def get_current_nfl_odds():
    with open(API_KEY_FILE, 'r') as file:
        API_KEY = file.readline()
    
    odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds', params={
        'api_key': API_KEY,
        'regions': REGIONS,
        'markets': MARKETS,
        'oddsFormat': ODDS_FORMAT,
        'dateFormat': DATE_FORMAT,
    })
    
    if odds_response.status_code != 200:
        msg = f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}'
        print(msg)
        raise OddsAPIException(msg)
    else:
        odds_json = odds_response.json()
        # Check the usage quota
        # print('Remaining requests', odds_response.headers['x-requests-remaining'])
        # print('Used requests', odds_response.headers['x-requests-used'])
        
    return odds_json

def get_and_write_current_nfl_odds():
    odds = get_current_nfl_odds()
    outfile = NFL_SEASON_DATA / f'odds-{int(time.time())}.json'
    with open(outfile, 'w') as file:
        json.dump(odds, file, indent=4)
        
    
if __name__ == "__main__":
    get_and_write_current_nfl_odds()