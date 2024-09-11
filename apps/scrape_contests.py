from dfsdata import dk_utils
from dfsscrape import draftkings, nfl, config, odds_api, stathead

CONTEST_RESULTS = True

if __name__ == "__main__":
    current_year = str(config.CURRENT_YEAR)
    draftkings.main(download_list=True)
    try:
        nfl.read_and_output_injury_report(nfl.URL_FUNCS[0], current_year, dk_utils.get_nfl_week(current_year), replace=True)
    except AttributeError as err:
        print('No injury report data found!')
    odds_api.get_and_write_current_nfl_odds()
    
    # scrape player stats
    stathead.read_and_output_all([dk_utils.CURRENT_YEAR], replace=True)
    
    # scrape draftkings contest results
    if CONTEST_RESULTS:
        draftkings.download_contest_entry_data()