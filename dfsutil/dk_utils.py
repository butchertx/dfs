import time
import pandas as pd
from typing import List
import pathlib

CURRENT_YEAR = '2024'

WEEK_ONE_STARTS = {'2020': 1599609600, '2021': 1630994400, '2022': 1662444000, '2023': 1693875600, '2024': 1725343200}
# Wed Sept 9 2020 at 12am
# Tue Sept 7 2021 at 1am
# Tue Sept 6 2022 at 1am
# Tue Sept 5 2023 at 1am
# Tue Sept 3 2024 at 1am

TEAM_NAME_FFA_DICT = {
    'LVR': 'LV',
    'JAC': 'JAX'
}

TEAM_NAME_STATHEAD_DICT = {

}


def get_nfl_week_(week_one_start, query_date):
    # query_date must be in seconds
    if query_date is None:
        current_time = time.time()
    else:
        current_time = query_date

    difference = current_time - week_one_start
    minutes = difference // 60
    hours = minutes // 60
    days = hours // 24
    weeks = days // 7
    # Fix the scheduling issue from Steelers vs. Ravens on Wed. Week 12, 2020
    if (week_one_start == WEEK_ONE_STARTS['2020']) and (weeks == 12) and (days == 0):
        return int(12)
    else:
        return int(weeks + 1)


def get_nfl_week(year: str, query_date: float = None):
    if year in WEEK_ONE_STARTS.keys():
        return get_nfl_week_(WEEK_ONE_STARTS[year], query_date)
    else:
        print('No valid year entered')


def get_cash_from_str(cash_str):
    return float(''.join(cash_str.lstrip('$').split(',')))


def read_fantasy_pros_projections(files: List[pathlib.Path]):
    players_fp_list = []
    for file in [str(f) for f in files]:
        temp_df = pd.read_csv(file).rename(columns={'PLAYER NAME': 'Player',
                                                    'TEAM': 'Team', 'PROJ. FPTS': 'fpros_projection'})
        temp_df['Player'] = [player.strip() for player in temp_df['Player']]
        temp_df['Pos'] = [file.split('_')[-2]]*len(temp_df)
        temp_df['week'] = [int(file.split('_')[-3])]*len(temp_df)
        players_fp_list.append(temp_df)

    return pd.concat(players_fp_list)


def read_ffanalytics_projections(files: List[pathlib.Path]):
    players_list = []
    positions = ['QB', 'RB', 'WR', 'TE', 'DST', 'K']

    def map_team_names(name):
        if name in TEAM_NAME_FFA_DICT.keys():
            return TEAM_NAME_FFA_DICT[name]
        else:
            return name

    for file in [str(f) for f in files]:
        temp_df = pd.read_csv(file).rename(columns={'player': 'Player', 'position': 'Pos',
                                                    'team': 'Team', 'points': 'projection_ppr'})
        temp_df = temp_df[temp_df['Pos'].isin(positions) & ~temp_df['Player'].isna()]
        temp_df['Player'] = [player.strip() for player in temp_df['Player']]
        temp_df['Team'] = temp_df['Team'].apply(map_team_names)
        temp_df['week'] = [int(file.split('_')[2].split('.')[0][2:])] * len(temp_df)
        players_list.append(temp_df)

    return pd.concat(players_list).drop(columns='Unnamed: 0')


def read_player_games(file: pathlib.Path):
    positions = ['QB', 'RB', 'WR', 'TE', 'DST', 'K']

    def map_team_names(name):
        if name in TEAM_NAME_STATHEAD_DICT.keys():
            return TEAM_NAME_STATHEAD_DICT[name]
        else:
            return name

    temp_df = pd.read_csv(file).rename(columns={'Pos.': 'Pos', 'team': 'Team', 'FantasyDKPt': 'fpts_ppr'})
    temp_df = temp_df[temp_df['Pos'].isin(positions) & ~temp_df['Player'].isna()]
    temp_df['Player'] = [player.strip() for player in temp_df['Player']]
    temp_df['Team'] = temp_df['Team'].apply(map_team_names)
    temp_df['fpts_ppr'] = temp_df['fpts_ppr'].fillna(0.0)

    return temp_df[['Player', 'Pos', 'Team', 'Week', 'fpts_ppr']]