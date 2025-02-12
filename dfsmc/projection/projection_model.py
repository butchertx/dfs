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

"""
import pandas as pd
import numpy as np
from typing import List

from dfsmc.projection.projection_data import ProjectionDataLoader
from dfsmc.projection.projection_data import PLAYER_ID_COLUMNS

    
class PlayerProjectionModel:
    
    # member data for model training
    data: pd.DataFrame
    target: pd.Series
    feature_names: np.ndarray
    target_names: np.ndarray
    
    def __init__(self):
        pass
    
    def load_data(self, year_range: List[int]):
        player_data = ProjectionDataLoader(year_range)
        player_data.prepare_data()
        self.data = player_data.prepared_data
        
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
    
class TrivialProjector(PlayerProjectionModel):
    
    id_without_week = [col for col in PLAYER_ID_COLUMNS if col != 'week_num']
    
    def __init__(self, year_range: List[int]):
        super().__init__()
        self.load_data(year_range)
        self.load_model()
        
    def load_model(self):
        """
        Compute the cummean of all players 'draftkings_points' for each week, each season
        save a new dataframe that will map year, name, week, team, pos to a point value
        
        The cummean here is inclusive of the current week, so for example a row with week_num 5
        will include the cummean of all weeks up to and including week 5.
        """
        grouped_by_year = self.data.groupby('year')
        for _, group in grouped_by_year:
            sorted = group.sort_values(by='week_num')
            cummean = sorted.groupby(self.id_without_week)['draftkings_points'].expanding().mean()
            idx_vals = [val[3] for val in cummean.index.values]
            self.data.loc[idx_vals, 'draftkings_points_cummean'] = cummean.values
        
    def get_projections(self, test_examples: pd.DataFrame, targets: List[str]) -> pd.DataFrame:
        """
        The trivial projector will simply return the cumulative season mean of the target.
        A player's first game of the season will be projected as 0 for all targets in the first iteration
        of this model. Future versions may be smarter and return the previous season's mean, the player's
        career mean, or a value based on the position of the player.
        
        test_examples minimal columns: ['year'] + ProjectionData.PLAYER_ID_COLUMNS
        """
        assert all([t in self.data.columns for t in targets]), 'Targets not in data!'
        test_examples = test_examples[['year'] + PLAYER_ID_COLUMNS].copy()
        self.data = self.data.sort_values(by=['year', 'week_num'], ascending=False)
        for year_week in zip(test_examples['year'].unique(), test_examples['week_num'].unique()):
            data_mask = (self.data['year'] == year_week[0]) & (self.data['week_num'] < year_week[1])
            cum_vals = self.data.loc[data_mask, ['draftkings_points_cummean'] + PLAYER_ID_COLUMNS].groupby(self.id_without_week).first()
            examples_mask = (test_examples['year'] == year_week[0]) & (test_examples['week_num'] == year_week[1])
            test_examples.loc[examples_mask, 'draftkings_points'] = test_examples.loc[examples_mask, self.id_without_week].apply(lambda x: cum_vals.loc[x, 'draftkings_points_cummean'], axis=0)
        pass
    
    def get_covariance(self) -> pd.DataFrame:
        return None
    
if __name__ == '__main__':
    trivial = TrivialProjector([2019])
    print(trivial.data.head())
    
    test_examples = trivial.data[['year'] + PLAYER_ID_COLUMNS].copy()[trivial.data['week_num'] == 16]
    print(test_examples.head())
    
    predictions = trivial.get_projections(test_examples, ['draftkings_points'])