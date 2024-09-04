from dfsdata.create_db import clean_dfs_tables
from dfsdata.update_tables.update_dfs_tables import DataWrangler
from dfsdata.interface import DFSDBInterface
from dfsdata.configure_db import DFS2024Config

MATCH_PLAYER_NAMES = True

if __name__ == "__main__":
    # Configure and Clean DFS Tables
    dfs_config = DFS2024Config()
    clean_dfs_tables(dfs_config)
    
    # Update Drafkings data
    wrangler = DataWrangler(DFSDBInterface(dfs_config))
    wrangler.insert_contests_2024()
    wrangler.insert_draftables()
    wrangler.insert_payouts()
    
    # Update other data
    # player name dictionary - Design Decision: All player names in DB should match Draftkings name + player ID
    if MATCH_PLAYER_NAMES:
        wrangler.match_player_names_2024()
    # injury reports
    # base projections
    wrangler.insert_fpros_projections()
    
    # NFL Data
    # clean_nfl_tables()
    # data_wrangler = SeasonData(DFSDBInterface(ini=defaultNFLConfig()))
    # data_wrangler.insert_player_games_data()
    # data_wrangler.insert_team_games_data()