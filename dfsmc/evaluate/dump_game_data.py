from dfsmc.projection import projection
import pandas as pd

if __name__ == "__main__":
    all_data = []
    for year in range(2017, 2024):
        projector = projection.TrivialProjector(year, None)
        data = projector.player_game_data.copy()
        data['year'] = [year]*len(data)
        all_data.append(data)
    all_data = pd.concat(all_data)
    all_data.to_csv('player_data.csv')