"""
Evaluate projections generated from different methods

Framework:
- Choose a scope (season(s)) and set of projection methods to compare
- Generate projections for all weeks/players in scope using all methods
- Compute RMSE and MAE (mean absolute error) for each method and prediction type (mean, median, etc.)


First step: let's try to get the "Most Likely Outcome" (MLO)
Then, when we have a pipeline for testing that, we can extend it to look
for upside, downside, and predicted player correlations.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pathlib
import os

from dfsmc.simulate import projection
from dfsutil.constants import SKILL_POSITIONS


PLOTS_OUT_PATH = pathlib.Path(os.path.join(pathlib.Path(__file__).parent.resolve(), 'plots_out'))

def RMSE(df):
    cols = df.columns
    return np.sqrt(np.sum(np.square(df[cols[0]].values - df[cols[1]].values)) / len(df))

def MAE(df):
    cols = df.columns
    return np.sum(np.abs(df[cols[0]].values - df[cols[1]].values)) / len(df)

def aggregations(df):
    return pd.Series([RMSE(df), MAE(df)], index=['RMSE', 'MAE'])

def plot_residuals(df: pd.DataFrame):
    if df.name in SKILL_POSITIONS:
        fig = plt.figure(dpi=200)
        plt.hist(df['fpts_dk'].values - df['fpts_dk_predicted'].values)
        plt.savefig(os.path.join(PLOTS_OUT_PATH, f'{df.name}.png'))

def get_projection_residuals(projector: projection.ResampleProjector):
    projections = projector.generate_projections().reset_index()
    results = projector.simulator.get_true_results(projector.season, projector.week)
    on_cols = ['player_name', 'pos', 'team']
    combined = pd.merge(projections[on_cols + ['mean']].rename(columns={'mean': 'fpts_dk_predicted'}), results[on_cols + ['fpts_dk']], on=on_cols, how='inner').dropna()
    return combined[['player_name', 'pos', 'team', 'fpts_dk_predicted', 'fpts_dk']].copy()
        

if __name__ == "__main__":
    
    for week in range(15,16):
        projector = projection.ResampleProjector(2022, week)
        predictions = get_projection_residuals(projector)
        grouped_by_pos = predictions.groupby('pos')[['fpts_dk_predicted', 'fpts_dk']]
        rmse_values = grouped_by_pos.apply(aggregations)
        print(rmse_values)
        
        grouped_by_pos.apply(plot_residuals)