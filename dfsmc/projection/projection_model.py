"""

A PlayerProjectionModel will take data loaded from 
PlayerProjectionData and train a model to generate projections.

The PlayerProjectionModel object will be a wrapper for different types
of models, such as linear regression, random forest, etc.

PlayerProjectionModel should produce estimates for the most likely outcome, the mean
outcome, and the variance of the outcome, when given a list of player/year/week queries.

The projections will be based on inference of a player's upcoming matchup. A given model
will require a set of fresh examples, whose columns will depend on what data is needed
in order to apply the model.


"CONCEPT DRIFT": https://arxiv.org/pdf/1010.4784
The concept class may change over time.
"""
import pandas as pd
import numpy as np
from typing import List
from itertools import product
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso, Lars
from sklearn.pipeline import Pipeline

from dfsmc.projection.projection_data import ProjectionDataLoader
from dfsmc.projection.projection_data import PLAYER_ID_COLUMNS, SCORING_COLUMNS, FANTASY_COLUMNS
from dfsmc.projection import metrics

ID_WITHOUT_WEEK = [col for col in PLAYER_ID_COLUMNS if col != 'week_num']
    
class PlayerProjectionModel:
    
    
    # member data for model training
    test_examples: pd.DataFrame
    target: pd.Series
    feature_names: np.ndarray
    target_names: np.ndarray
    
    def __init__(self):
        pass
    
    def load_data(self, year_range: List[int]):
        if year_range is None:
            year_range = list(range(2017, 2023))
        player_data = ProjectionDataLoader(year_range)
        player_data.prepare_data()
        self.raw_data = player_data.prepared_data
        
    def get_projections(self, test_examples: pd.DataFrame, targets: List[str]) -> pd.DataFrame:
        """
        test_examples will be a dataframe containing columns with the necessary
        features for whichever model is making the projections. 
        """
        raise NotImplementedError('Projections are not implemented!')
    
    def get_covariance(self) -> pd.DataFrame:
        """
        Should return the covariance matrix. Assume get_projections has
        already populated the player projections
        """
        raise NotImplementedError('Covariance model is not implemented!')
    
    @staticmethod
    def compute_cumulative(game_data: pd.DataFrame, cumul_columns: List[str], mean_func: str) -> pd.DataFrame:
        """
        game_data should be PlayerProjectionModel.data
        cumul_columns should be the columns to compute the cumulative average for
        mean_func should be 'mean' or 'median' for computing the cumulative average by week
        """
        idx_cols = ['name_display', 'year', 'week_num']
        other_idx_cols = ['team_name_abbr', 'pos_game']
        cumul_columns = list(set(cumul_columns))
        new_cumul_columns = [f'{col}_cumul_{mean_func}' for col in cumul_columns]
        all_cols = idx_cols + other_idx_cols + cumul_columns
        assert all([t in game_data.columns for t in idx_cols]), f'Index columns not in data!: {idx_cols}'
        assert all([t in game_data.columns for t in cumul_columns]), f'Desired cumulative columns not in data!: {cumul_columns}'
        
        cumulative = game_data.copy()[all_cols].sort_values(by=idx_cols)
        grouped_by_year = cumulative.groupby('year')
        for _, group in grouped_by_year:
            sorted = group.sort_values(by='week_num')
            cumavg = sorted.groupby(ID_WITHOUT_WEEK)[cumul_columns].expanding().agg(mean_func)
            idx_vals = [val[3] for val in cumavg.index.values]
            cumulative.loc[idx_vals, new_cumul_columns] = cumavg.values
        
        # fill in missing weeks for each player
        uniques = [cumulative[col].unique() for col in idx_cols]
        idx_vals = product(*uniques)
        index_vals = pd.MultiIndex.from_tuples(list(idx_vals), names=idx_cols)
        cumulative = cumulative.set_index(idx_cols).reindex(index_vals).reset_index().sort_values(by=idx_cols)
        cumulative = cumulative[all_cols + new_cumul_columns].copy()
        for new_col in new_cumul_columns + other_idx_cols:
            cumulative[new_col] = cumulative.groupby('name_display')[new_col].ffill()
            if new_col in new_cumul_columns:
                cumulative[new_col] = cumulative.groupby('name_display')[new_col].shift(1)
            else:
                cumulative[new_col] = cumulative.groupby('name_display')[new_col].bfill()
        cumulative = cumulative[all_cols + new_cumul_columns].copy()
        return cumulative
    
class TrivialProjector(PlayerProjectionModel):
    
    
    def __init__(self, year_range: List[int] = None):
        super().__init__()
        self.load_data(year_range)
        self.load_model()
        
    def load_model(self, cumul_func: str = 'mean'):
        """
        Compute the cummean of all players 'draftkings_points' for each week, each season
        save a new dataframe that will map year, name, week, team, pos to a point value
        """
        # Calculate cumsum for each player
        self.test_examples = self.compute_cumulative(self.raw_data, ['draftkings_points'], cumul_func)
        self.test_examples = self.test_examples.rename(columns={'draftkings_points': 'draftkings_points_actual'})
        self.test_examples = self.test_examples.rename(columns={f'draftkings_points_cumul_{cumul_func}': 'draftkings_points'})
        self.test_examples = self.test_examples.set_index(['year'] + PLAYER_ID_COLUMNS)
        print(self.test_examples.index.names)
        print(self.test_examples.columns)
        
    def get_projections(self, test_examples: pd.DataFrame) -> pd.DataFrame:
        """
        The trivial projector will simply return the cumulative season mean of the target.
        A player's first game of the season will be projected as 0 for all targets in the first iteration
        of this model. Future versions may be smarter and return the previous season's mean, the player's
        career mean, or a value based on the position of the player.
        
        test_examples minimal columns: ['year'] + ProjectionData.PLAYER_ID_COLUMNS
        """
        return self.test_examples.loc[test_examples.index].fillna(0)
    
    def get_covariance(self) -> pd.DataFrame:
        return None

class RegressionProjector(PlayerProjectionModel):
    
    scale_and_pca = Pipeline([('scaler', StandardScaler()), ('pca', PCA(n_components=3))])
    
    QB_cols = ['pass_att', 'pass_sacked', 'rush_att', 'rush_td', 'pass_cmp', 'pass_yds', 'pass_td', 'pass_int', 'fumbles', 'draftkings_points']
    
    def __init__(self, regressor = LinearRegression(), year_range: List[int] = None):
        super().__init__()
        self.regressor = regressor
        self.load_data(year_range)
        self.load_model()
        
    def load_model(self):
        # QBS
        qb_df = self.raw_data.loc[self.raw_data['pos_game'] == 'QB', :].copy()
        qb_df['pass_yds'] = qb_df['pass_yds_per_cmp'] * qb_df['pass_cmp']
        cum_columns = self.QB_cols
        cumul_df = self.compute_cumulative(qb_df, cum_columns, 'mean')
        cumul_df['draftkings_points_actual'] = cumul_df['draftkings_points']
        self.test_examples = cumul_df.drop(columns=cum_columns).rename(columns={f'{col}_cumul_mean': col for col in cum_columns}).dropna()
        self.features, self.target = self.test_examples[cum_columns].values, self.test_examples['draftkings_points_actual'].values
        self.pca_result = self.scale_and_pca.fit_transform(self.features)
        self.model = self.regressor.fit(self.pca_result, self.target)
        print(self.test_examples.index.names)
        print(self.test_examples.columns)
    
    def get_projections(self, test_examples: pd.DataFrame) -> pd.DataFrame:
        features = test_examples[self.QB_cols].values
        pca_result = self.scale_and_pca.transform(features)
        return pd.DataFrame(self.model.predict(pca_result), index=test_examples.index, columns=['draftkings_points'])
    
    def get_covariance(self) -> pd.DataFrame:
        pass

def train_and_eval_model(model: PlayerProjectionModel):
    test_examples = model.test_examples.copy().reset_index().set_index(['year'] + PLAYER_ID_COLUMNS)
    target = test_examples[['draftkings_points_actual']].rename(columns={'draftkings_points_actual': 'draftkings_points'})
    
    predictions = model.get_projections(test_examples)
    
    results, residuals = metrics.evaluate_projections(predictions['draftkings_points'], target, metrics.RMSE)
    return results

if __name__ == '__main__':
    ####### Trivial
    results = train_and_eval_model(TrivialProjector())
    print(results)
    
    ####### Linear
    results = train_and_eval_model(RegressionProjector(LinearRegression()))
    print(results)
    
    ## Logistic needs some modifications and the others just use different loss functions that don't change the results for such a simple model
    
    # ####### Logistic
    # results = train_and_eval_model(RegressionProjector(LogisticRegression()))
    # print(results)
    
    # ####### Ridge
    # results = train_and_eval_model(RegressionProjector(Ridge()))
    # print(results)
    
    # ####### Lasso
    # results = train_and_eval_model(RegressionProjector(Lasso()))
    # print(results)
    
    # ####### Lars
    # results = train_and_eval_model(RegressionProjector(Lars()))
    # print(results)