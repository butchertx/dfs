"""
The projection interface should ingest upcoming matchup data
(player, pos, team, opponent)
and produce projections for the players by some metric.

The bare minimum is to produce an expected projection and covariance,
but an ideal, complete solution would provide more information on the distribution of outcomes
for each player, relative to their teammates and opponents.
"""
import pandas as pd

from dfsmc.simulate import games

class ResampleProjector:
    
    """
    Make projections for players in a single week.
    Use a ResampleSimulator to sample from previous weeks
    in the same season.
    """
    
    def __init__(self, season: int, week: int):
        self.season = season
        self.week = week
        self.simulator = games.ResampleSimulator()
        
    def generate_projections(self):
        """
        Realistically, we don't need to do this stochastically.
        We can just compute all the values deterministically from the available data.
        """
        # resampled = self.simulator.generate_multiple(num_samples=100, season=self.season, week_num=self.week)
        resampled = self.simulator.get_games_data(self.season, self.week)
        grouped = resampled.groupby(['player_name', 'pos', 'team'])['fpts_dk'].agg(['median', 'mean', 'std', 'min', 'max'])
        return grouped

if __name__ ==  "__main__":
    projector = ResampleProjector(2022, 10)
    print(projector.generate_projections().head(10))