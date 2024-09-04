from dfsdata import dk_utils
from dfsscrape import draftkings, nfl, config

if __name__ == "__main__":
    current_year = config.CURRENT_YEAR
    draftkings.main(download_list=True)
    nfl.read_and_output_injury_report(current_year, dk_utils.get_nfl_week(current_year), replace=True)