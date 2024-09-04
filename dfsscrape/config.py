import pathlib

NFL_SEASON_DATA = pathlib.Path('D:/Data/DFS/NFL_SEASON_DATA/')
# DATA_DUMP_2022 = 'F:/DFS/NFL_DFS/2022/draftkings_data/'
# DATA_DUMP_2023 = pathlib.Path('D:/Data/DFS/2023/draftkings_data/')
# CURRENT_YEAR = 2023
DATA_DUMP_2024 = pathlib.Path('D:/Data/DFS/2024/draftkings_data/')
CURRENT_YEAR = 2024

class NoDataException(Exception):
    pass

class ScrapingConfig:

    _year: int
    _dk_data_path: pathlib.Path

    def __init__(self, year: int = 2024):
        if year == 2024:
            self._year = year
            self._dk_data_path = DATA_DUMP_2024
        else:
            raise NotImplementedError('Only 2024 is implemented for draftkings config')

    @property
    def year(self):
        return self._year

    @property
    def dk_data_path(self):
        return self._dk_data_path

