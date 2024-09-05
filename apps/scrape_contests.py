from dfsdata import dk_utils
from dfsscrape import draftkings, nfl, config, odds_api

if __name__ == "__main__":
    current_year = str(config.CURRENT_YEAR)
    draftkings.main(download_list=True)
    nfl.read_and_output_injury_report(nfl.URL_FUNCS[0], current_year, dk_utils.get_nfl_week(current_year), replace=True)
    odds_api.get_and_write_current_nfl_odds()