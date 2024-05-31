from dfsdata.create_db import clean_nfl_tables
from dfsdata.update_tables.update_season_data import SeasonData
from dfsdata.interface import DFSDBInterface
from dfsdata.configure_db import defaultNFLConfig

if __name__ == "__main__":
    clean_nfl_tables()
    data_wrangler = SeasonData(DFSDBInterface(ini=defaultNFLConfig()))
    data_wrangler.insert_player_games_data()
    data_wrangler.insert_team_games_data()