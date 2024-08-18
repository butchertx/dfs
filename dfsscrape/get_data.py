import pathlib
import pandas as pd

def get_data_path():
    parent_dir = pathlib.Path(__file__).parent.resolve()
    filepath = parent_dir / 'data'
    return filepath

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
    return pd.read_csv(file)

def get_team_games_data(year: str):
    file = get_data_path() / f'nfl_team_games_{year}.csv'
    return pd.read_csv(file)