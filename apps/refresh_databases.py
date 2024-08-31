from dfsdata.create_db import clean_dfs_tables
from dfsdata import update_tables
from dfsdata.interface import DFSDBInterface
from dfsdata.configure_db import DFSdbConfig, DFS_CONFIG_INI_2024, defaultNFLConfig

if __name__ == "__main__":
    # DFS Data
    dfs_config = DFSdbConfig(DFS_CONFIG_INI_2024)
    clean_dfs_tables(dfs_config)
    wrangler = update_tables.DataWrangler(DFSDBInterface(dfs_config))
    wrangler.insert_contests_2024()
    
    # NFL Data
    # clean_nfl_tables()
    # data_wrangler = SeasonData(DFSDBInterface(ini=defaultNFLConfig()))
    # data_wrangler.insert_player_games_data()
    # data_wrangler.insert_team_games_data()