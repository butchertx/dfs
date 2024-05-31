import pathlib
from typing import Generator

from dfsdata import configure_db


class TeamGameNames:
    
    _data_path: pathlib.Path
    
    def __init__(
        self,
        data_path: pathlib.Path = configure_db.defaultNFLConfig().DATA_PATH
    ):
        self._data_path = data_path
        
    @property
    def data_path(self):
        return self._data_path
    
    @staticmethod
    def filename_to_season(filepath: pathlib.Path) -> int:
        return int(str(filepath).split('_')[-1].split('.')[0])
    
    def player_games(self):
        return self.data_path.glob('player_games_*.csv')
    
    def team_games(self):
        return self.data_path.glob('team_games_*.csv')

class ContestDataNames:

    _dk_path: pathlib.Path
    _fpros_path: pathlib.Path
    _projections_path: pathlib.Path
    _player_game_path: pathlib.Path

    def __init__(
        self,
        dk_path: pathlib.Path = configure_db.defaultDFSConfig().DK_PATH,
        data_path: pathlib.Path = configure_db.defaultDFSConfig().DATA_PATH,
        repo_path: pathlib.Path = configure_db.defaultDFSConfig().REPO_DATA_PATH
    ):
        self._dk_path = dk_path
        self._fpros_path = data_path
        self._player_game_path = repo_path

    @property
    def dk_path(self):
        return self._dk_path

    @property
    def projections_path(self):
        return self._projections_path

    @property
    def player_game_path(self):
        return self._player_game_path

    def contest_table_files(self) -> Generator[pathlib.Path, None, None]:
        return self._dk_path.glob('contest_table_2023-*.csv')

    def contest_details_files(self) -> Generator[pathlib.Path, None, None]:
        return self._dk_path.glob('contest_details-*.json')

    def draft_group_files(self) -> Generator[pathlib.Path, None, None]:
        return self._dk_path.glob('draft_group_info-*.json')

    def fpros_files(self) -> Generator[pathlib.Path, None, None]:
        return (self._fpros_path / 'projections').glob('FantasyPros*.csv')

    def projections_files(self):
        return (self._fpros_path / 'projections').glob('projections*.csv')

    def player_game_file(self, year: int) -> pathlib.Path:
        return self.player_game_path / f'player_games_{str(year)}.csv'

    @staticmethod
    def filename_to_id(filepath: pathlib.Path) -> int:
        return int(str(filepath).split('-')[1].split('.')[0])

    def contest_details_(self, filepath: pathlib.Path) -> int:
        return self.filename_to_id(filepath)

    def draft_group_details_filename_to_id(self, filepath: pathlib.Path) -> int:
        return self.filename_to_id(filepath)
