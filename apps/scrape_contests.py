from argparse import ArgumentParser

from dfsdata import dk_utils
from dfsscrape import draftkings, nfl, config, odds_api, stathead

if __name__ == "__main__":
    
    parser = ArgumentParser()
    parser.add_argument('-s', '--stats', help='Download player stats', action='store_true', dest='stats', default=False)
    parser.add_argument('-r', '--results', help='Download previous week DK contest results', action='store_true', dest='results', default=False)
    args = parser.parse_args()
    CONTEST_RESULTS = args.results
    PLAYER_STATS = args.stats
    
    current_year = str(config.CURRENT_YEAR)
    draftkings.main(download_list=True)
    try:
        nfl.read_and_output_injury_report(nfl.URL_FUNCS[0], current_year, dk_utils.get_nfl_week(current_year), replace=True)
    except AttributeError as err:
        print('No injury report data found!')
    odds_api.get_and_write_current_nfl_odds()
    
    # scrape player stats
    if PLAYER_STATS:
        stathead.read_and_output_all([dk_utils.CURRENT_YEAR], replace=True)
    
    # scrape draftkings contest results
    if CONTEST_RESULTS:
        draftkings.download_contest_entry_data()