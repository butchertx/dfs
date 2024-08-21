from dfsmc.simulate import projection

ID_COLUMNS = [
    'team_name_abbr', 'game_num', 'opp_name'
]

CATEGORICAL_INPUTS = [
    'game_location'
]

CATEGORICAL_RESULTS = [
    'cover', 'ou_result'
]

NUMERICAL_INPUTS = [
    'over_under', 'vegas_line'
]

NUMERICAL_RESULTS = [
    'duration', 'plays_defense', 'plays_offense', 'points', 'points_combined', 'points_diff', 'points_opp', 'time_of_posession', 'tot_yds', 'yds_per_play_defense', 'yds_per_play_offense'
]

if __name__ == "__main__":
    projector = projection.ProjectionModel(2022, None)
    
    df = projector.player_game_data.copy()
    df = df.replace({'TE/QB': 'TE'}) # just make Taysom Hill a TE
    dk_points_totals_by_position = df.groupby(by=['team_name_abbr', 'game_num', 'pos_game'])['draftkings_points'].sum()
    dk_points_totals_by_team = df.groupby(by=['team_name_abbr', 'game_num'])['draftkings_points'].sum()
    print(dk_points_totals_by_position.head(10))
    print(dk_points_totals_by_team.head(10))
    dk_points = dk_points_totals_by_position.reset_index().pivot(index=['team_name_abbr', 'game_num'], columns=['pos_game'])
    dk_points.columns = [f'{val[1]}_points' for val in dk_points.columns]
    dk_points['Total_points'] = dk_points_totals_by_team
    print(dk_points.head(10))