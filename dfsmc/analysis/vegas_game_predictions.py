import pandas as pd
import numpy as np
import datetime
# import matplotlib.pyplot as plt

from dfsmc.simulate import projection
from dfsutil import files

pd.set_option('display.max_columns', 100)

ID_COLUMNS = [
    'team_name_abbr', 'game_num', 'week_num'
]

CATEGORICAL_INPUTS = [
    'game_location', 'opp_name_abbr'
]

CATEGORICAL_RESULTS = [
    'cover', 'ou_result'
]

NUMERICAL_INPUTS = [
    'over_under', 'vegas_line'
]

NUMERICAL_RESULTS = [
    'duration', 'plays_defense', 'plays_offense', 'points', 'points_combined', 'points_diff', 'points_opp',
    'time_of_poss', 'tot_yds', 'yds_per_play_defense', 'yds_per_play_offense',
    'QB_dk_points', 'RB_dk_points', 'TE_dk_points', 'WR_dk_points', 'K_dk_points', 'Offense_dk_points'
]

def combine_home_away(df_teams: pd.DataFrame):
    # combine team-based rows into game-based rows
    df_home, df_away = df_teams[df_teams['is_home']], df_teams[~df_teams['is_home']]
    dk_columns = ['QB_dk_points', 'RB_dk_points', 'TE_dk_points', 'WR_dk_points', 'K_dk_points', 'Offense_dk_points']
    
    # columns to keep in the away DF
    keep_columns_away = [
        'team_name_abbr', 'week_num', 'game_num', 'plays_defense', 'plays_offense', 'time_of_poss', 'tot_yds', 'yds_per_play_defense', 'yds_per_play_offense'
    ] + dk_columns
    keep_columns_away_dict = {col: f'{col}_away' for col in keep_columns_away}
    df_away = df_away[keep_columns_away].rename(columns=keep_columns_away_dict)
    
    # Columns to keep in the home DF
    keep_columns_home = [
        'team_name_abbr', 'week_num', 'game_num', 'opp_name_abbr', 'cover', 'plays_defense', 'plays_offense',
        'ou_result', 'over_under', 'vegas_line', 'duration', 'points_combined',
        'points', 'points_opp', 'points_diff', 'time_of_poss', 'tot_yds', 'yds_per_play_defense', 'yds_per_play_offense'
    ] + dk_columns
    keep_columns_home_dict = {col: f'{col}_home' for col in keep_columns_home}
    df_home = df_home[keep_columns_home].rename(columns=keep_columns_home_dict)
    
    # Columns to drop in merged DF
    drop_columns = [
        'plays_defense_away', 'plays_offense_away', 'yds_per_play_offense_away', 'yds_per_play_defense_away',
        'week_num_away', 'team_name_abbr_away'
    ]
    
    # Columns to rename in merged DF
    rename_columns = {
        'week_num_home': 'week_num',
        'opp_name_abbr_home': 'team_name_abbr_away',
        'cover_home': 'cover',
        'points_opp_home': 'points_away',
        'points_combined_home': 'points_combined',
        'points_diff_home': 'points_diff',
        'yds_per_play_defense_home': 'yds_per_play_defense',
        'yds_per_play_offense_home': 'yds_per_play_offense',
        'ou_result_home': 'ou_result',
        'over_under_home': 'over_under',
        'vegas_line_home': 'vegas_line',
        'duration_home': 'duration'
    }
    
    df_games = df_home.merge(df_away, left_on=['opp_name_abbr_home', 'week_num_home'], right_on=['team_name_abbr_away', 'week_num_away'])
    df_games = df_games.drop(columns=drop_columns).rename(columns=rename_columns)
    
    # Add calculated columns
    df_games['Game_dk_points'] = df_games['Offense_dk_points_home'] +  df_games['Offense_dk_points_away']
    
    return df_games

def set_cumulative_averages(df: pd.DataFrame):
    """
    df is df_teams - easier to group by team
    """
    # add some columns
    df['vs_spread'] = df['points_diff'] + df['vegas_line'] # vegas_line < 0 is favored, points_diff is team_points - opp_points
    df['implied_points'] = 0.5*(df['over_under'] - df['vegas_line'])
    
    CUM_COLUMNS = [
        'vs_spread', 'implied_points', 'plays_defense', 'plays_offense', 'yds_per_play_offense', 'yds_per_play_defense',
        'points', 'points_combined'
    ] + ['QB_dk_points', 'RB_dk_points', 'TE_dk_points', 'WR_dk_points', 'K_dk_points', 'Offense_dk_points']
    
    df = df.sort_values(by='game_num', ascending=True)
    
    def add_cummean(df):
        for val in df.columns:
            df[f'{val}_cum'] = df[val].expanding().mean()
        df['sum_helper'] = [True]*len(df)
        df['game_num'] = df['sum_helper'].cumsum()
        return df.drop(columns=['sum_helper'])
        
    df = df.groupby(['team_name_abbr'])[CUM_COLUMNS].apply(add_cummean).reset_index().drop(columns=['level_1'])
    print(df.head(100))
    
    return df

def get_data(year):
    projector = projection.ProjectionModel(year, None, output_data=True)
    
    df = projector.player_game_data.copy()
    df = df.replace({'TE/QB': 'TE'}) # just make Taysom Hill a TE
    dk_points_totals_by_position = df.groupby(by=['team_name_abbr', 'game_num', 'pos_game'])['draftkings_points'].sum()
    dk_points_totals_by_team = df.groupby(by=['team_name_abbr', 'game_num'])['draftkings_points'].sum()
    # print(dk_points_totals_by_position.head(10))
    # print(dk_points_totals_by_team.head(10))
    dk_points = dk_points_totals_by_position.reset_index().pivot(index=['team_name_abbr', 'game_num'], columns=['pos_game'])
    dk_points.columns = [f'{val[1]}_dk_points' for val in dk_points.columns]
    dk_points['Offense_dk_points'] = dk_points_totals_by_team
    # print(dk_points.head(10))
    
    df = df.merge(dk_points, left_on=['team_name_abbr', 'game_num'], right_index=True).drop(columns=['name_display', 'pos_game']).drop_duplicates(subset=['team_name_abbr', 'game_num'])
    df = df[ID_COLUMNS + CATEGORICAL_INPUTS + CATEGORICAL_RESULTS + NUMERICAL_INPUTS + NUMERICAL_RESULTS]
    df = df.T.drop_duplicates().T.sort_values(by='week_num', ascending=True).reset_index().drop(columns=['index']) # drop duplicate columns and sort
    
    # clean some data types
    df['duration'] = [60*float(val.split(':')[0]) + float(val.split(':')[1]) for val in df['duration'].values] # float minutes
    df['time_of_poss'] = [float(val.split(':')[0]) + float(val.split(':')[1])/60. for val in df['time_of_poss'].values] # float minutes
    df[NUMERICAL_INPUTS + NUMERICAL_RESULTS] = df[NUMERICAL_INPUTS + NUMERICAL_RESULTS].astype(float).fillna(0.0)
    
    # Add computed columns
    df['game_location'] = df['game_location'].fillna('')
    df['is_home'] = np.not_equal(df['game_location'].values, ['@'])
    
    # get combined games dataframe
    df_teams = df.copy()
    df_games = combine_home_away(df_teams)
    
    return df_teams, df_games

def distribution_vs_spread(df: pd.DataFrame):
    cover, nocover, push = df[df['cover'] == 'covered'], df[df['cover'] == 'did not cover'], df[df['cover'] == 'push']
    print(cover.describe())
    print(nocover.describe())
    print(push.describe())
    
    # plt.figure()
    
    # plt.scatter(cover['points_diff'].values, cover['vegas_line'].values)
    # plt.show()
    
if __name__ == "__main__":
    df, _ = get_data(2022)
    df.to_csv(files.get_parent_path(__file__) / 'team_games.csv')
    print(df[NUMERICAL_RESULTS].describe(percentiles=[]))
    
    set_cumulative_averages(df)