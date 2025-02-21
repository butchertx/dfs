"""
The projection interface should ingest upcoming matchup data
(player, pos, team, opponent)
and produce projections for the players by some metric.

The bare minimum is to produce an expected projection and covariance,
but an ideal, complete solution would provide more information on the distribution of outcomes
for each player, relative to their teammates and opponents.
"""
import pandas as pd
import numpy as np
from typing import Type, List
from itertools import product
import pathlib
import os

from dfsdata.interface import DFSDBInterface
from dfsmc.simulate import games
from dfsscrape import get_data as gd
from dfsutil import constants, transform

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
ALL_COLUMNS = PLAYER_ID_COLUMNS + FANTASY_COLUMNS + SCORING_COLUMNS + PLAYER_STAT_COLUMNS + TEAM_STAT_COLUMNS

class PlayerProjectionData:
    
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
    
    
    def __init__(self, season: int, week: int, output_data: bool = False):
        self.season = season
        self.week = week
        self.get_data()
        self.combine_and_filter_data(output_data)
        
    def get_projections(self, players: pd.DataFrame = None, filter_stat_thresholds = True) -> pd.DataFrame:
        """
        Should return a dataframe for player projections with columns: PLAYER_ID_COLUMNS + FANTASY_COLUMNS
        These represent MEAN outcomes: along with the assumption of a Gamma distribution and covariance,
        the full probability distribution should be constructible
        
        (Eventually) Should also return a (sparse) covariance matrix
        """
        raise NotImplementedError('Projections are not implemented!')
    
    def get_covariance(self) -> pd.DataFrame:
        """
        Should return the covariance matrix. Assume get_projections has
        already populated the player projections
        """
        raise NotImplementedError('Covariance model is not implemented!')
    
    def get_all_data(self):
        return self.player_game_data.copy()[ALL_COLUMNS]
    
    def get_actuals(self, players: pd.Series = None):
        if players is not None:
            players_included = self.player_game_data.merge(players, on=['name_display', 'week_num'], how='inner')
            data = self.player_game_data.loc[self.player_game_data['name_display'].isin(players_included['name_display'])].copy()
        else:
            data = self.player_game_data.copy()
        return data[PLAYER_ID_COLUMNS + FANTASY_COLUMNS + ['rush_att', 'pass_att', 'targets']]
    
    def apply_stat_thresholds(self):
        self.player_game_data[['pass_att', 'rush_att', 'targets']] = self.player_game_data[['pass_att', 'rush_att', 'targets']].fillna(0.0)
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
            if not all([col in col_names for col in PLAYER_ID_COLUMNS]) \
                and not all([col in col_names for col in TEAM_ID_COLUMNS]):
                print('Error: Data does not have all required player columns')
                print(f'Table: {attr_name}')
                exit(1)
        
    def combine_and_filter_data(self, output_data=False):
        player_data_columns = FANTASY_COLUMNS + SCORING_COLUMNS + PLAYER_STAT_COLUMNS
        all_team_columns = TEAM_ID_COLUMNS + TEAM_STAT_COLUMNS
        
        # get dataframe combining player data, using only unique columns
        player_dfs = []
        for attr_name in self.player_data_attrs:
            # if len(player_data_columns_remaining) > 0:
            column_subset = PLAYER_ID_COLUMNS + player_data_columns
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
        data_columns = [col for col in player_data_combined if col not in PLAYER_ID_COLUMNS]
        player_data_combined = player_data_combined.loc[player_data_combined[data_columns].dropna(how='all').index]
        team_cols = [col for col in all_team_columns if col not in player_data_combined.columns]
        self.player_game_data = player_data_combined.merge(self.team_games_data[TEAM_ID_COLUMNS + team_cols], on=['week_num', 'team_name_abbr'], how='left')
        self.player_game_data['week_num'] = self.player_game_data['week_num'].astype(int)
        self.player_game_data['game_location'] = self.player_game_data['game_location'].fillna('')
        
        # remove duplicate columns
        self.player_game_data = self.player_game_data.loc[:,~self.player_game_data.columns.duplicated()].copy()
        if output_data:
            self.player_game_data.to_csv(f'player_data_{self.season}.csv')
    
    def list_unaccounted_columns(self):
        col_list = []
        player_cols_accounted = PLAYER_ID_COLUMNS + FANTASY_COLUMNS + SCORING_COLUMNS + PLAYER_STAT_COLUMNS
        team_cols_accounted = TEAM_ID_COLUMNS + TEAM_STAT_COLUMNS
        print(len(player_cols_accounted + team_cols_accounted) - 2)
        print(len(list(set(player_cols_accounted + team_cols_accounted))))
        for attr_name in self.data_attrs:
            col_names = getattr(self, attr_name).columns
            col_list.append(col_names)
        unaccounted = sorted(list(set([col_name for col_vals in col_list for col_name in col_vals if col_name not in player_cols_accounted + team_cols_accounted])))
        return unaccounted
    
    def populate_upcoming_matchups(self, draft_group_id: int):
        """
        Populate player_data with missing matchups given a draft group id
        
        Need new columns 
        ['name_display', 'team_name_abbr', 'pos_game', 'game_location', 'opp_name_abbr']
        """
        query = """
            SELECT
            draft.name, draft.position, draft.team_abbreviation,
            comp.home_team_abbreviation, comp.away_team_abbreviation
            FROM draftables draft
            JOIN competitions comp
            ON draft.competition_id = comp.id
            WHERE draft.draft_group_id = %s
        """
        db_interface = DFSDBInterface()
        results = db_interface.run_format_command(query, (draft_group_id,))
        results['week_num'] = [self.week]*len(results)
        home = results['home_team_abbreviation'].values[0]
        away = results['away_team_abbreviation'].values[0]
        opp_dict = {home: away, away: home}
        rename_cols = {
            'name': 'name_display',
            'team_abbreviation': 'team_name_abbr',
            'position': 'pos_game'
        }
        results = results.rename(columns=rename_cols)
        results['opp_name_abbr'] = results['team_name_abbr'].map(opp_dict)
        results['game_location'] = ['']*len(results)
        results.loc[results['team_name_abbr'] == away, 'game_location'] = ['@']*len(results.loc[results['team_name_abbr'] == away, 'game_location'])
        drop_cols = ['home_team_abbreviation', 'away_team_abbreviation']
        self.player_game_data = pd.concat([self.player_game_data, results.drop(columns=drop_cols)], ignore_index=True)
        return self.player_game_data
    
    @staticmethod
    def str_name():
        raise NotImplementedError()
    
    @staticmethod
    def cov_model_path():
        raise NotImplementedError()
    
    def read_covariance(self):
        infile = self.cov_model_path()
        return pd.read_csv(infile, index_col='Unnamed: 0')

class TrivialProjector(PlayerProjectionData):
    
    """
    Projections are the player's season cumulative mean
    """
    
    def get_projections(self, player_list: pd.DataFrame):
        """
        player_list should have name and week as columns, and each row corresponds to a week to project
        
        future (True) is to populate the current or next week's matchups from the database
        """
        if self.week is None:
            # print('Warning! Trivial Projector was not initialized with a week number so it is projecting for all available weeks')
            weekly_results = []
            for week in range(1,19):
                self.week = week
                weekly_results.append(self.get_projections(player_list.loc[player_list['week_num']==week].copy()))
            self.week = None # reset the week value
            return pd.concat(weekly_results).drop_duplicates().reset_index().drop(columns='index')
        
        # Get only rows with players that have data for the specified week
        players_matched = self.player_game_data.loc[self.player_game_data['name_display'].isin(player_list['name_display']), 'name_display'].values # self.player_game_data.merge(player_list, on=['name_display', 'week_num'], how='inner')['name_display']
        cumulative_df = self.player_game_data.loc[(self.player_game_data['week_num'] < self.week) & self.player_game_data['name_display'].isin(players_matched)].copy()
        means = cumulative_df.groupby(['name_display'])['draftkings_points'].mean().reset_index()
        means = means.merge(
                self.player_game_data.loc[self.player_game_data['week_num'] == self.week, ['name_display', 'team_name_abbr', 'pos_game', 'game_location', 'opp_name_abbr']].drop_duplicates(),
                on='name_display'
            )
        means['week_num'] = [self.week]*len(means)
        self.projections = means.copy()
        return means
    
    def get_covariance(self) -> pd.DataFrame:
        proj = self.projections
        cov = pd.read_csv(self.cov_model_path())
    
    @staticmethod
    def str_name():
        return 'TrivialProjector'
    
    @staticmethod
    def cov_model_path():
        return pathlib.Path(__file__).parent / 'models' / f'covariance_{TrivialProjector.str_name()}.csv'
    
class FantasyProsProjector(PlayerProjectionData):
    
    """
    Here we just pull the projections straight from the database
    """
    
    def get_projections(self, player_list: pd.DataFrame):
        """
        player_list should have name and week as columns, and each row corresponds to a week to project
        """
    
class ResampleProjector(PlayerProjectionData):
    
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

class ProjectionDataLoader:
    
    def __init__(self, season_range: List[int]):
        self.season_range = season_range

    def prepare_data(self):
        """
        Example call:
        get_projections(range(2017,2023), TrivialProjector))
        """
        player_data = []
        for year in self.season_range:
            projector = PlayerProjectionData(year, week=None, output_data=False)
            projector.apply_stat_thresholds()
            # projections_temp = projector.get_projections(projector.player_game_data[['name_display', 'week_num']].copy())
            actuals_temp = projector.get_all_data()

            # projections_temp['year'] = [year]*len(projections_temp)
            # projections_temp['week_num'] = projections_temp['week_num'].astype(int)
            # projections_temp = projections_temp.rename(columns={'draftkings_points': 'draftkings_points_predicted'})
            actuals_temp['year'] = [year]*len(actuals_temp)

            # projections_temp = projections_temp.merge(actuals_temp, on=['year', 'week_num', 'team_name_abbr', 'pos_game', 'name_display'], how='inner')
            # projections.append(projections_temp)
            player_data.append(actuals_temp)
        results = pd.concat(player_data).dropna(subset=['draftkings_points'])
        self.prepared_data = results.reset_index().drop(columns='index')
        return results.copy()
    
    def get_residuals(self):
        if not hasattr(self, 'prepared_data'):
            self.prepare_data()
        self.prepared_data['res'] = self.prepared_data['draftkings_points'] - self.prepared_data['draftkings_points_predicted']
        return self.prepared_data.copy()
    
    def get_gamma(self):
        def shift_zero(vals) -> pd.Series:
            shift = np.min(vals)
            vals = vals - np.min(vals)
            return vals, shift
        
        if not hasattr(self, 'prepared_data'):
            self.prepare_data()
        if 'res' not in self.prepared_data.columns:
            self.get_residuals()
        position_groups = self.prepared_data.groupby('pos_game')['res']
        results = {}
        for pos, ser in position_groups:
            shift = np.min(ser)
            mean = np.mean(ser - shift)
            sigma = np.std(ser - shift)
            results[pos] = (mean**2 / sigma**2, mean / sigma**2, shift) # alpha, beta
        return results
    
    @staticmethod
    def _sum_points_by_team_week(df: pd.DataFrame):
        """
        Meant to by used in groupby.apply()
        
        Assume groupby is by year, week_num, team.
        Sum up all columns (points, predicted, and res, probably?) by position
        """
        columns = ['draftkings_points', 'draftkings_points_predicted', 'res']
        by_position = df.groupby('pos_game')[columns].sum()
        new_row_dict = {val: [by_position.loc[val[0], val[1]]] for val in product(by_position.index.values, by_position.columns)}
        return pd.DataFrame(new_row_dict)
    
    @staticmethod
    def _match_team_games(df: pd.DataFrame):
        """
        For missing teams, we'll fill the values with means instead of NaNs to keep the existing
        teams data in the analysis
        """
        # merge on home/away
        df['home'] = (df['game_location'] != '@')
        df = df.drop(columns=[('game_location', '')])
        home = df.loc[df['home']].drop(columns=('home', '')).rename(columns={'team_name_abbr': 'home_team', 'opp_name_abbr': 'away_team'})
        away = df.loc[~df['home']].drop(columns=('home', '')).rename(columns={'team_name_abbr': 'away_team', 'opp_name_abbr': 'home_team'})
        doubled = home.merge(away, on=[('home_team', ''), ('away_team', '')], suffixes=['_home', '_away'], how='outer')
        
        # fill nan columns
        num_columns = [col for col in doubled.columns if col not in [('home_team', ''), ('away_team', '')]]
        doubled[num_columns] = doubled[num_columns].fillna(doubled[num_columns].mean())
        
        return doubled
    
    def get_player_game_covariance(self, column='res', output_results=False):
        """
        NOTE: there are a bunch of missing team-games so we usually only have
        28-30 on a given week, even before BYEs. The analysis doesn't require 32
        per week but it would be nice to figure out where we're losing these team-games.
        Example: TAM is missing from column 'team_name_abbr' for 2017 week 2
        """
        if not hasattr(self, 'prepared_data'):
            self.prepare_data()
        if 'res' not in self.prepared_data.columns:
            self.get_residuals()
        
        # sum each team
        pos_sums = self.prepared_data.groupby(by=['year', 'week_num', 'team_name_abbr', 'game_location', 'opp_name_abbr']).apply(self._sum_points_by_team_week, include_groups=False)
        pos_sums.index = pos_sums.index.droplevel(-1)
        pos_sums = pos_sums.reset_index()
        
        # match each team with opponent
        game_sums = pos_sums.groupby(by=['year', 'week_num']).apply(self._match_team_games, include_groups=False)
        game_sums.index = game_sums.index.droplevel(-1)
        # game_sums = game_sums.reset_index()
        
        # reconfigure columns and compute covariance
        game_sums = game_sums.loc[:, game_sums.columns.get_level_values(1) == column]
        game_sums.columns = game_sums.columns.droplevel(-1)
        covar = game_sums.cov()
        corr = game_sums.corr()
        if output_results:
            outdir = pathlib.Path(__file__).parent / 'models'
            os.makedirs(outdir, exist_ok=True)
            outfile = self.model_type.cov_model_path()
            covar.to_csv(outfile)
            
        return covar, corr

if __name__ ==  "__main__":
    
    # Test Cases
    # Pull data for a single season
    # make sure all the columns exist and are populated
    player_data = ProjectionDataLoader([2023])
    player_data.prepare_data()
    print(player_data.prepared_data.columns)
    print(len(player_data.prepared_data))
    print(len(player_data.prepared_data[['name_display', 'year', 'week_num']].drop_duplicates()))
    print(player_data.prepared_data.loc[player_data.prepared_data['pos_game'] == 'WR', ['name_display', 'year', 'week_num', 'rec', 'rec_yds_per_rec', 'rec_td', 'draftkings_points']].sort_values(by='draftkings_points', ascending=False).head(20))
    
    # Do the same for multiple seasons
    player_data = ProjectionDataLoader(range(2017, 2024))
    player_data.prepare_data()
    print(player_data.prepared_data.columns)
    print(len(player_data.prepared_data))
    print(len(player_data.prepared_data[['name_display', 'year', 'week_num']].drop_duplicates()))
    print(player_data.prepared_data.loc[player_data.prepared_data['pos_game'] == 'WR', ['name_display', 'year', 'week_num', 'rec', 'rec_yds_per_rec', 'rec_td', 'draftkings_points']].sort_values(by='draftkings_points', ascending=False).head(20))
    