import numpy as np
import pandas as pd

from dfsdata.interface import DFSDBInterface
from dfsdata import configure_db

class GameSimulator:
    """ Docstring for GameSimulator
    """
    
    @property
    def db_interface(self):
        return self._db_interface
    
    @db_interface.setter
    def db_interface(self, db_ini_file: configure_db.DBConfig):
        self._db_interface = DFSDBInterface(db_ini_file)
    
    def __init__(self, db_ini_file: configure_db.DBConfig = configure_db.defaultNFLConfig()):
        self.db_interface = db_ini_file
        self._games_rng = np.random.default_rng()
        
class ResampleSimulator(GameSimulator):
    """Simulate matchup outcomes by resampling from the full season
    
    the product of this class should be a list of dataframes
    (could be a single dataframe with an instance index) listing player
    identifiers and fantasy points.
    
    ingests: csv or dataframe with player-games through a season
    outputs: dataframe with players and points for each trial
    configuration:
    - number of samples
    """
    
    def __init__(self, db_ini_file: configure_db.DBConfig = configure_db.defaultNFLConfig()):
        super().__init__(db_ini_file=db_ini_file)
        
    def get_games_data(self, season: int = None, week_num: int = None):
        """
        Get player points totals for each week before week_num.  If 
        week_num is None, pull data from the whole season
        """
        data_df = pd.DataFrame()
        if season is None:
            if week_num is None:
                query = "SELECT player_name, pos, team, week_num, fpts_dk FROM player_games"
                data_df = self.db_interface.run_command(query)
            else:
                query = "SELECT player_name, pos, team, week_num, fpts_dk FROM player_games WHERE week_num < %s"
                data_df = self.db_interface.run_format_command(query, (week_num,))
        else:
            if week_num is None:
                query = "SELECT player_name, pos, team, week_num, fpts_dk FROM player_games WHERE season = %s"
                data_df = self.db_interface.run_format_command(query, (season,))
            else:
                query = "SELECT player_name, pos, team, week_num, fpts_dk FROM player_games WHERE season = %s AND week_num < %s"
                data_df = self.db_interface.run_format_command(query, (season, week_num))
        return data_df
    
    def get_true_results(self, season: int = None, week_num: int = None):
        """
        Get player points totals for week_num.  If 
        week_num is None, pull data from the whole season
        """
        data_df = pd.DataFrame()
        if season is None:
            if week_num is None:
                query = "SELECT player_name, pos, team, week_num, fpts_dk FROM player_games"
                data_df = self.db_interface.run_command(query)
            else:
                query = "SELECT player_name, pos, team, week_num, fpts_dk FROM player_games WHERE week_num = %s"
                data_df = self.db_interface.run_format_command(query, (week_num,))
        else:
            if week_num is None:
                query = "SELECT player_name, pos, team, week_num, fpts_dk FROM player_games WHERE season = %s"
                data_df = self.db_interface.run_format_command(query, (season,))
            else:
                query = "SELECT player_name, pos, team, week_num, fpts_dk FROM player_games WHERE season = %s AND week_num = %s"
                data_df = self.db_interface.run_format_command(query, (season, week_num))
        data_df['fpts_dk'] = data_df['fpts_dk'].astype(float)
        return data_df
    
    def games_generator(self, season: int = None, week_num: int = None):
        """
        Get a generator that returns a DataFrame of player outcomes corresponding to random weeks of season, before week_num
        """
        if season is None or week_num is None:
            raise NotImplementedError("games_generator only works with a specified season and week number")
        games_data = self.get_games_data(season, week_num)
        while True:
            try:
                random_week = self._games_rng.integers(low=1, high=week_num, size=1)[0]
                yield games_data.loc[games_data['week_num'] == random_week].copy()
            except StopIteration:
                break
            
    def generate_multiple(self, num_samples: int, season: int = None, week_num: int = None):
        generator = self.games_generator(season, week_num)
        results_list = []
        for iter in range(num_samples):
            sample = next(generator)
            sample['sample_idx'] = [iter]*len(sample)
            results_list.append(sample)
        return pd.concat(results_list)

if __name__ == "__main__":
    simulator = ResampleSimulator()
    games_data = simulator.get_games_data(season=2022)
    generator = simulator.games_generator(season=2022, week_num=10)
    print(next(generator).head(10))
    print(next(generator).head(10))
    print(next(generator).head(10))
    print(next(generator).head(10))