from configparser import ConfigParser
import psycopg2
from psycopg2 import extras
import pandas as pd
import pathlib
from typing import List, Dict

from dfsdata import configure_db as db_config_module


class DFSDBInterface:

    db_args: Dict
    db_config: db_config_module.DBConfig

    def __init__(self, ini: db_config_module.DBConfig = db_config_module.defaultDFSConfig()):
        self.db_args = self.config(ini.INI)
        self.db_config = ini
        self.conn = psycopg2.connect(**self.db_args)
        self.cur = self.conn.cursor()

    def __del__(self):
        if self.cur is not None:
            self.cur.close()
        if self.conn is not None:
            self.conn.close()

    def config(self, filename, section='postgresql'):
        # create a parser
        parser = ConfigParser()
        # read config file
        parser.read(filename)

        # get section, default to postgresql
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))

        return db

    def run_command(self, command, fetch=True):
        result = None
        try:
            self.cur.execute(command)
            if fetch:
                result = self.cur.fetchall()
                columns = [elt[0] for elt in self.cur.description]
                result = pd.DataFrame(result, columns=columns)
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        return result

    def run_commands(self, commands: List[str]):
        """
        Run several commands, no output

        :param commands: list of str commands
        """
        try:
            for command in commands:
                self.cur.execute(command)
                self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def run_format_command(self, command, variable, fetch=True):
        result = None
        try:
            self.cur.execute(command, variable)
            if fetch:
                result = self.cur.fetchall()
                columns = [elt[0] for elt in self.cur.description]
                result = pd.DataFrame(result, columns=columns)
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        return result

    def run_format_insert(self, command: str, data: List[tuple]) -> None:
        try:
            extras.execute_values(self.cur, command, data, template=None, page_size=100)
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            
    def run_sql_file(self, filepath: pathlib.Path) -> None:
        try:
            with self.cur as cursor:
                cursor.execute(open(filepath, 'r').read())
            self.conn.commit()
        except Exception as error:
            print(error)
    
if __name__ == "__main__":
    games_db = DFSDBInterface()