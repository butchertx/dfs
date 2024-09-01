from dfsdata.create_db import clean_dfs_tables
from dfsdata.update_tables.update_dfs_tables import DataWrangler
from dfsdata.interface import DFSDBInterface
from dfsdata.configure_db import DFS2024Config

if __name__ == "__main__":
    # DFS Data
    dfs_config = DFS2024Config()
    clean_dfs_tables(dfs_config)
    wrangler = DataWrangler(DFSDBInterface(dfs_config))
    wrangler.insert_contests_2024()
    wrangler.insert_draftables()
    
    # NFL Data
    # clean_nfl_tables()
    # data_wrangler = SeasonData(DFSDBInterface(ini=defaultNFLConfig()))
    # data_wrangler.insert_player_games_data()
    # data_wrangler.insert_team_games_data()