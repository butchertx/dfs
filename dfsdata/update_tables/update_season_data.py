import pandas as pd

from dfsdata import configure_db, interface, path_name


class SeasonData:
    
    _db: interface.DFSDBInterface
    _path_names: path_name.TeamGameNames

    def __init__(self, db: interface.DFSDBInterface):
        self._db = db
        self._path_names = path_name.TeamGameNames()
        
    @property
    def db(self):
        return self._db
    
    @property
    def path_names(self):
        return self._path_names

    def insert_player_games_data(self):
        player_files = self.path_names.player_games()
        def read_file(file: str):
            data = pd.read_csv(file)
            data['season'] = [self.path_names.filename_to_season(file)]*len(data)
            data['home_team'] = data['Unnamed: 14'] != '@'
            return data
        
        players_table = pd.concat([read_file(f) for f in player_files])
        
        # For now let's just insert all every time
        if len(players_table) > 0:
            player_game_command = """INSERT into player_games (
                player_name, pos, fpts_dk, season, game_num, week_num, date, team, opp_team, home_team
                )
                values %s
                ON CONFLICT DO NOTHING
                """
            
            # Prepare and insert player-game data
            columns = [
                'Player', 'Pos.', 'FantasyDKPt', 'season', 'Game_num', 'Week_num', 'Date', 'Team', 'Opp', 'home_team'
            ]
            players_table = players_table[columns]
            data_to_insert = [tuple(row.values.tolist()) for idx, row in players_table.iterrows()]
            self.db.run_format_insert(player_game_command, data_to_insert)
        else:
            print('Error: No player-game data read')
            exit(1)
            
    def insert_team_games_data(self):
        team_files = self.path_names.team_games()
        def read_file(file: str):
            data = pd.read_csv(file)
            data['season'] = [self.path_names.filename_to_season(file)]*len(data)
            data['home_team'] = data['Unnamed: 13'] != '@'
            return data
        
        teams_table = pd.concat([read_file(f) for f in team_files])
        
        # For now let's just insert all every time
        if len(teams_table) > 0:
            player_game_command = """INSERT into team_games (
                team, date, pts, td, over_under, day, game_num, week_num, season, opp_team, home_team, result
                )
                values %s
                ON CONFLICT DO NOTHING
                """
            
            # Prepare and insert player-game data
            columns = [
                'Team', 'Date', 'Pts', 'TD', 'Over/Under', 'Day', 'G#', 'Week', 'season', 'Opp', 'home_team', 'Result'
            ]
            teams_table = teams_table[columns]
            data_to_insert = [tuple(row.values.tolist()) for idx, row in teams_table.iterrows()]
            self.db.run_format_insert(player_game_command, data_to_insert)
        else:
            print('Error: No player-game data read')
            exit(1)

if __name__ == "__main__":
    data_wrangler = SeasonData(interface.DFSDBInterface(ini=configure_db.defaultNFLConfig()))
    data_wrangler.insert_player_games_data()
    data_wrangler.insert_team_games_data()