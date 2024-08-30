import pandas as pd
import numpy as np

def cumulative_mean(df: pd.DataFrame, fill_value: float = np.nan, add_mean: bool = False, add_game_num: bool = True):
    """
    Insert the cumulative mean of all columns of df
    
    Assume the data has already been grouped and/or sorted
    """
    plain_cols = df.columns
    for val in plain_cols:
        df[f'{val}_cum'] = df[val].expanding().mean()
        if add_mean is not None:
            df[f'{val}_mean'] = [df[val].mean()]*len(df[val])
    df['sum_helper'] = [True]*len(df)
    df['game_num'] = df['sum_helper'].cumsum()
    df['prev_games'] = df['game_num'] - [1]*len(df)
    df.loc[df['prev_games'] < 0.5, 'prev_games'] = fill_value
    for val in plain_cols:
        df[f'{val}_cum'] = (df[f'{val}_cum']*df['game_num'] - df[val]) / df['prev_games']
    
    if add_game_num:
        return df.drop(columns=['sum_helper', 'prev_games'])
    else:
        return df.drop(columns=['sum_helper', 'prev_games', 'game_num'])
    
def cumulative_mean_no_game_num(df: pd.DataFrame):
    return cumulative_mean(df, add_game_num=False)