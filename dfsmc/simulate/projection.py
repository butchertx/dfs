"""
The projection interface should ingest upcoming matchup data
(player, pos, team, opponent)
and produce projections for the players by some metric.

The bare minimum is to produce an expected projection and covariance,
but an ideal, complete solution would provide more information on the distribution of outcomes
for each player, relative to their teammates and opponents.
"""
import pandas as pd
from typing import Type

from dfsmc.simulate import games
from dfsscrape import get_data as gd
from dfsutil import constants, transform
    
class ProjectionModel:
    
    """
    We want to project the median, upper and lower quartile, and covariance of fantasy points for all players
    in a single game. For the initial implementation, we will only consider players on the same team:
    QB, RBs, WRs, and TEs.
    A full implementation will also consider opposing players in the same game, team defenses, and Kickers.
    
    The best way to do this is probably to estimate the stats that give fantasy points:
    
    Passing:
    Completions - event
    Yds/Completion - float
    Passing TDs - event
    Passing 2pt conversions - event
    Int - event
    
    Receiving:
    Receptions - event
    Yds/Reception - float
    Rec TDs - event
    Rec 2pt - event
    Fmbl - event
    
    Rushing:
    Att - event
    Yds/Rush - float
    Rush TDs - event
    Rush 2pt - event
    Fmbl - event
    
    Bonus:
    Rec yds total - event
    Rush yds total - event
    Pass yds total - event
    
    """
    PLAYER_ID_COLUMNS = ['name_display', 'week_num', 'team_name_abbr', 'pos_game']
    TEAM_ID_COLUMNS = ['week_num', 'date', 'team_name_abbr', 'game_location', 'opp_name_abbr']
    FANTASY_COLUMNS = ['draftkings_points']
    SCORING_COLUMNS = [
        'rush_att', 'rush_yds_per_att', 'rush_td', 'rec', 'rec_yds_per_rec', 'rec_td', 'two_pt_md',
        'pass_cmp', 'pass_yds_per_cmp', 'pass_td', 'pass_int', 'fumbles', 'fumbles_rec_td', 'all_td' 
    ]
    PLAYER_STAT_COLUMNS = [
        'pass_adj_net_yds_per_att', 'pass_air_yds_per_att', 'pass_att', 'pass_blitzed', 'pass_hurried', 'pass_on_target_pct',
        'pass_play_action', 'pass_poor_throw_pct', 'pass_pressured_pct', 'pass_rpo', 'pass_sacked', 'pass_tgt_yds_per_att',
        'pocket_time', 'touches', 'catch_pct', 'targets',
        'rec_adot', 'rec_air_yds_per_rec', 'rec_drop_pct', 'rec_yac_per_rec', 'rec_yds_per_tgt',
        'rush_scrambles_yds_per_att', 'rush_yds_bc_per_rush'
    ]
    TEAM_STAT_COLUMNS = [
        'cover', 'duration', 'game_day_of_week', 'game_num', 'game_result', 'ou_result', 'over_under',
        'plays_defense', 'plays_offense', 'points', 'points_combined', 'points_diff', 'points_opp',
        'time_of_poss', 'tot_yds', 'vegas_line', 'yds_per_play_defense', 'yds_per_play_offense'
    ]
    
    def __init__(self, season: int, week: int, output_data: bool = False):
        self.season = season
        self.week = week
        self.get_data()
        self.combine_and_filter_data(output_data)
        
    def get_projections(self, players: pd.Series = None) -> pd.DataFrame:
        """
        Should return a dataframe for player projections with columns: PLAYER_ID_COLUMNS + FANTASY_COLUMNS
        These represent MEAN outcomes: along with the assumption of a Gamma distribution and covariance,
        the full probability distribution should be constructible
        
        (Eventually) Should also return a (sparse) covariance matrix
        """
        raise NotImplementedError('Projections are not implemented!')
    
    def get_actuals(self, players: pd.Series = None):
        if players is not None:
            data = self.player_game_data.loc[self.player_game_data['name_display'].isin(players)].copy()
        else:
            data = self.player_game_data.copy()
        return data[self.PLAYER_ID_COLUMNS + self.FANTASY_COLUMNS]
    
    def apply_stat_thresholds(self):
        self.player_game_data.drop(
                self.player_game_data[(self.player_game_data['pos_game'] == 'QB') & (self.player_game_data['pass_att'] < 10)].index,
                inplace=True
            )
        
        self.player_game_data.drop(
                self.player_game_data[(self.player_game_data['pos_game'] == 'RB') & (self.player_game_data['rush_att'] < 5)].index,
                inplace=True
            )
        
        self.player_game_data.drop(
                self.player_game_data[(self.player_game_data['pos_game'] == 'WR') & (self.player_game_data['targets'] < 1)].index,
                inplace=True
            )
        
        self.player_game_data.drop(
                self.player_game_data[(self.player_game_data['pos_game'] == 'TE') & (self.player_game_data['targets'] < 1)].index,
                inplace=True
            )
    
    def get_data(self):
        self.passing_data = gd.get_passing_data(self.season)
        self.passing_adv_data = gd.get_passing_adv_data(self.season)
        self.rushing_data = gd.get_rushing_data(self.season)
        self.receiving_data = gd.get_receiving_data(self.season)
        self.skill_adv_data = gd.get_receiving_rushing_adv_data(self.season)
        self.snap_counts_data = gd.get_snap_counts_data(self.season)
        self.fantasy_pts_data = gd.get_fantasy_pts_data(self.season)
        self.team_games_data = gd.get_team_games_data(self.season)
        self.data_attrs = [
            'passing_data', 'passing_adv_data', 'rushing_data', 'receiving_data',
            'skill_adv_data', 'snap_counts_data', 'fantasy_pts_data', 'team_games_data'
        ]
        self.player_data_attrs = [
            'passing_data', 'passing_adv_data', 'rushing_data', 'receiving_data',
            'skill_adv_data', 'snap_counts_data', 'fantasy_pts_data'
        ]
        for attr_name in self.data_attrs:
            col_names = getattr(self, attr_name).columns
            if not all([col in col_names for col in self.PLAYER_ID_COLUMNS]) \
                and not all([col in col_names for col in self.TEAM_ID_COLUMNS]):
                print('Error: Data does not have all required player columns')
                print(f'Table: {attr_name}')
                exit(1)
        
    def combine_and_filter_data(self, output_data=False):
        player_data_columns = self.FANTASY_COLUMNS + self.SCORING_COLUMNS + self.PLAYER_STAT_COLUMNS
        all_team_columns = self.TEAM_ID_COLUMNS + self.TEAM_STAT_COLUMNS
        
        # get dataframe combining player data, using only unique columns
        player_dfs = []
        for attr_name in self.player_data_attrs:
            # if len(player_data_columns_remaining) > 0:
            column_subset = self.PLAYER_ID_COLUMNS + player_data_columns
            current_attr = getattr(self, attr_name).copy()
            attr_columns = [str(col) for col in current_attr.columns.values]
            current_slice = current_attr[[col for col in column_subset if col in attr_columns]]
            player_dfs.append(current_slice)
            # player_data_columns_remaining = [col_name for col_name in player_data_columns_remaining if col_name not in current_slice]
        player_data_combined = player_dfs[0]
        for df in player_dfs[1:]:
            common_cols = [name for name in set(list(df.columns.values) + list(player_data_combined.columns.values)) if name in df.columns.values and name in player_data_combined.columns.values]
            player_data_combined = pd.merge(player_data_combined, df, on=common_cols, how='outer')
        # print(list(set(player_data_combined['pos_game'].values)))
        player_data_combined = player_data_combined.replace({'TE/QB': 'TE'}) # just make Taysom Hill a TE
        player_data_combined = player_data_combined[player_data_combined['pos_game'].isin(constants.OFFENSE_POSITIONS)]
        player_data_combined = player_data_combined.drop_duplicates()
        # remove empty rows
        data_columns = [col for col in player_data_combined if col not in self.PLAYER_ID_COLUMNS]
        player_data_combined = player_data_combined.loc[player_data_combined[data_columns].dropna(how='all').index]
        team_cols = [col for col in all_team_columns if col not in player_data_combined.columns]
        self.player_game_data = player_data_combined.merge(self.team_games_data[self.TEAM_ID_COLUMNS + team_cols], on=['week_num', 'team_name_abbr'], how='left')
        self.player_game_data['week_num'] = self.player_game_data['week_num'].astype(int)
        if output_data:
            self.player_game_data.to_csv(f'player_data_{self.season}.csv')
    
    def list_unaccounted_columns(self):
        col_list = []
        player_cols_accounted = self.PLAYER_ID_COLUMNS + self.FANTASY_COLUMNS + self.SCORING_COLUMNS + self.PLAYER_STAT_COLUMNS
        team_cols_accounted = self.TEAM_ID_COLUMNS + self.TEAM_STAT_COLUMNS
        print(len(player_cols_accounted + team_cols_accounted) - 2)
        print(len(list(set(player_cols_accounted + team_cols_accounted))))
        for attr_name in self.data_attrs:
            col_names = getattr(self, attr_name).columns
            col_list.append(col_names)
        unaccounted = sorted(list(set([col_name for col_vals in col_list for col_name in col_vals if col_name not in player_cols_accounted + team_cols_accounted])))
        return unaccounted
    
class TrivialProjector(ProjectionModel):
    
    """
    Projections are the player's season cumulative mean
    """
    
    def get_projections(self, player_list: pd.Series):
        if self.week is None:
            print('Warning! Trivial Projector was not initialized with a week number so it is projecting for all available weeks')
            weekly_results = []
            for week in range(1,19):
                self.week = week
                weekly_results.append(self.get_projections(player_list))
            return pd.concat(weekly_results).drop_duplicates().reset_index().drop(columns='index')
        cumulative_df = self.player_game_data.loc[(self.player_game_data['week_num'] < self.week) & self.player_game_data['name_display'].isin(player_list)].copy()
        means = cumulative_df.groupby(['name_display'])['draftkings_points'].mean().reset_index()
        means = means.merge(self.player_game_data[['name_display', 'team_name_abbr', 'pos_game']].drop_duplicates(), on='name_display')
        means['week_num'] = [self.week]*len(means)
        return means
    
class ResampleProjector(ProjectionModel):
    
    """
    Make projections for players in a single week.
    Use a ResampleSimulator to sample from previous weeks
    in the same season.
    """
    
    def __init__(self, season: int, week: int):
        self.season = season
        self.week = week
        self.simulator = games.ResampleSimulator()
        
    def get_projections(self):
        """
        Realistically, we don't need to do this stochastically.
        We can just compute all the values deterministically from the available data.
        """
        # resampled = self.simulator.generate_multiple(num_samples=100, season=self.season, week_num=self.week)
        resampled = self.simulator.get_games_data(self.season, self.week)
        grouped = resampled.groupby(['player_name', 'pos', 'team'])['fpts_dk'].agg(['median', 'mean', 'std', 'min', 'max'])
        return grouped
        
def get_projections(data_range, projector_obj: Type[ProjectionModel]):
    """
    Example call:
    get_projections(range(2017,2023), TrivialProjector))
    """
    projections = []
    for year in data_range:
        projector = projector_obj(year, week=None, output_data=True)
        projector.apply_stat_thresholds()
        projections_temp = projector.get_projections(projector.player_game_data['name_display'].values)
        actuals_temp = projector.get_actuals()
        
        projector.player_game_data['dk_sq'] = projector.player_game_data['draftkings_points']**2
        print(projector.player_game_data.sort_values(by='dk_sq', ascending=True)[projector.PLAYER_ID_COLUMNS + projector.FANTASY_COLUMNS].head(20))
        projections_temp['dk_sq'] = projections_temp['draftkings_points']**2
        print(projections_temp.sort_values(by='dk_sq', ascending=True)[projector.PLAYER_ID_COLUMNS + projector.FANTASY_COLUMNS].head(20))
        actuals_temp['dk_sq'] = actuals_temp['draftkings_points']**2
        print(actuals_temp.sort_values(by='dk_sq', ascending=True)[projector.PLAYER_ID_COLUMNS + projector.FANTASY_COLUMNS].head(20))

        projections_temp['year'] = [year]*len(projections_temp)
        projections_temp = projections_temp.rename(columns={'draftkings_points': 'draftkings_points_predicted'})
        actuals_temp['year'] = [year]*len(actuals_temp)

        projections_temp = projections_temp.merge(actuals_temp, on=['year', 'week_num', 'team_name_abbr', 'pos_game', 'name_display'], how='inner')
        projections.append(projections_temp)
    results = pd.concat(projections).dropna(subset=['draftkings_points_predicted', 'draftkings_points'])
    results['res'] = results['draftkings_points_predicted'] - results['draftkings_points']
    results['res_sq'] = results['res']**2
    results = results.sort_values(by='res_sq', ascending=True).reset_index().drop(columns=['index']).drop_duplicates()
    return results

if __name__ ==  "__main__":
    projections = get_projections(range(2017,2023), TrivialProjector)
    print(projections.head(100))