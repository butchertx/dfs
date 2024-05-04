

class GameSimulator:
    """ Docstring for GameSimulator
    """
    
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        self._x = value
    
    def __init__(self):
        self.x = 1
        
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
    
    def __init__():
        pass