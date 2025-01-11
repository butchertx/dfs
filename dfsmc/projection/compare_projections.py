from dfsmc.projection import projection_data
from dfsmc.evaluate.eval_projections import RMSE, MAE, aggregations

if __name__ == "__main__":
    projection_trainer = projection_data.ProjectionModelTrainer(list(range(2017,2024)), projection_data.TrivialProjector)
    projection_trainer.prepare_data()
    print(projection_trainer.prepared_data.columns)
    print(len(projection_trainer.prepared_data))
    print(len(projection_trainer.prepared_data[['name_display', 'year', 'week_num']].drop_duplicates()))
    print(projection_trainer.prepared_data.sort_values(by='draftkings_points', ascending=False).head(100))
    
    grouped_by_pos = projection_trainer.prepared_data.groupby('pos_game')[['draftkings_points_predicted', 'draftkings_points']]
    rmse_values = grouped_by_pos.apply(aggregations)
    print(rmse_values)