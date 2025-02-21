import pandas as pd
import numpy as np

def RMSE(predicted: pd.DataFrame, actual: pd.DataFrame):
    """
    assume predicted and actual have matching indices. Compute the metric on all common columns
    """
    combined = actual.merge(predicted, left_index=True, right_index=True, how='left', suffixes=('_actual', '_predicted')).fillna(0.)
    col_base_names = ['_'.join(name.split('_')[:-1]) for name in combined.columns if name.endswith('_actual')]
    error_cols = []
    for col in col_base_names:
        if f'{col}_actual' in combined.columns and f'{col}_predicted' in combined.columns:
            combined[f'{col}_error'] = combined[f'{col}_predicted'] - combined[f'{col}_actual']
            error_cols.append(f'{col}_error')
    result = {}
    for col in error_cols:
        result[col.rstrip('_error')] = (combined[col] ** 2).mean() ** 0.5
    return result, combined[error_cols]

def evaluate_projections(predicted: pd.DataFrame, actual: pd.DataFrame, metric: callable):
    """
    Compute the metric, split out by each position
    """
    all, all_res = metric(predicted, actual)
    actual = actual.reset_index(level='pos_game')
    predicted = predicted.reset_index(level='pos_game')
    pos_groups = actual['pos_game'].unique()
    results = {
        'all': all
    }
    residuals = {
        'all': all_res
    }
    for group_name in pos_groups:
        results[group_name], residuals[group_name] = metric(predicted.loc[predicted['pos_game'] == group_name].drop(columns=['pos_game']), actual.loc[actual['pos_game'] == group_name].drop(columns=['pos_game']))
    return results, residuals
    
if __name__ == "__main__":
    pass