import pathlib
import pandas as pd

from dfsscrape.config import ScrapingConfig

CONFIG = ScrapingConfig()

def get_data_path():
    return CONFIG.nfl_data_path

def get_passing_data(year: str):
    file = get_data_path() / f'nfl_player_games_passing_{year}.csv'
    return pd.read_csv(file)

def get_passing_adv_data(year: str):
    file = get_data_path() / f'nfl_player_games_passing_adv_{year}.csv'
    return pd.read_csv(file)

def get_rushing_data(year: str):
    file = get_data_path() / f'nfl_player_games_rushing_{year}.csv'
    return pd.read_csv(file)

def get_receiving_data(year: str):
    file = get_data_path() / f'nfl_player_games_receiving_{year}.csv'
    return pd.read_csv(file)

def get_receiving_rushing_adv_data(year: str):
    file = get_data_path() / f'nfl_player_games_receiving_rushing_adv_{year}.csv'
    return pd.read_csv(file)

def get_snap_counts_data(year: str):
    file = get_data_path() / f'nfl_player_games_snap_counts_{year}.csv'
    return pd.read_csv(file)

def get_fantasy_pts_data(year: str):
    file = get_data_path() / f'nfl_player_games_fantasy_{year}.csv'
    df = pd.read_csv(file)
    # throw kickers in there too
    kicker_file = get_data_path() / f'nfl_player_games_kicking_fg_{year}.csv'
    kicker_df = pd.read_csv(kicker_file)
    kicker_df = kicker_df[['name_display', 'team_name_abbr', 'game_num', 'week_num', 'game_location', 'opp_name_abbr', 'draftkings_points', 'pos_game']].drop_duplicates()
    return pd.concat([df, kicker_df])

def get_team_games_data(year: str):
    file = get_data_path() / f'nfl_team_games_{year}.csv'
    return pd.read_csv(file)