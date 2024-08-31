import pathlib, os

DFS_CONFIG_INI_2024 = pathlib.Path(__file__).parent.resolve() / 'ini' / 'database_2024.ini'

class DBConfig:

    _INI: pathlib.Path  # database .ini file
    _DATA_PATH: pathlib.Path  # local path to data
    
    def __init__(self, inifile: pathlib.Path):
        self._INI = inifile
        
    @property
    def INI(self):
        return self._INI
    
    @property
    def DATA_PATH(self):
        return self._DATA_PATH


class DFSdbConfig(DBConfig):
    
    _YEAR: str  # NFL season
    _DK_PATH: pathlib.Path  # local path to DK data
    _REPO_DATA_PATH: pathlib.Path  # path to repo data directory

    def __init__(self, inifile: pathlib.Path):
        super().__init__(inifile)

    @property
    def YEAR(self):
        return self._YEAR

    @property
    def REPO_DATA_PATH(self):
        return self._REPO_DATA_PATH

    @property
    def DK_PATH(self):
        return self._DK_PATH
    
class defaultDFSConfig(DFSdbConfig):

    def __init__(self):
        inifile = pathlib.Path(__file__).parent.resolve() / 'database_test_2024.ini'
        super().__init__(inifile)
        thisfile = pathlib.Path(__file__).parent.resolve()
        self._YEAR = '2024'
        self._DATA_PATH = pathlib.Path(os.path.join(thisfile, 'sample_data'))
        self._DK_PATH = pathlib.Path(os.path.join(thisfile, 'sample_data'))
        self._REPO_DATA_PATH = pathlib.Path(os.path.join(thisfile, 'sample_data'))


class NFLdbConfig(DBConfig):

    def __init__(self, inifile: pathlib.Path):
        super().__init__(inifile)

class defaultNFLConfig(NFLdbConfig):
    
    def __init__(self, inifile: pathlib.Path = pathlib.Path(__file__).parent.resolve() / 'games_data_test.ini'):
        super().__init__(inifile)
        thisfile = pathlib.Path(__file__).parent.resolve()
        self._DATA_PATH = pathlib.Path(os.path.join(thisfile, 'sample_data'))