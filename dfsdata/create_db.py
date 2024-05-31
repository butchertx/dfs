import psycopg2
import argparse
import pathlib

from dfsdata.interface import DFSDBInterface
from dfsdata import configure_db


def drop_nfl_tables(config_in: configure_db.NFLdbConfig = configure_db.defaultNFLConfig()):
    try:
        db_interface = DFSDBInterface(config_in)

        commands = [
            "DROP TABLE IF EXISTS player_games",
            "DROP TABLE IF EXISTS team_games",
        ]

        db_interface.run_commands(commands)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def clean_nfl_tables(config_in: configure_db.NFLdbConfig = configure_db.defaultNFLConfig()):
    drop_nfl_tables(config_in)
    create_nfl_tables(config_in)

def create_nfl_tables(config_in: configure_db.NFLdbConfig = configure_db.defaultNFLConfig()):
    """ create tables in the PostgreSQL database"""
    try:
        db_interface = DFSDBInterface(config_in)
        db_interface.run_sql_file(pathlib.Path(__file__).parent.resolve() / 'sql' / 'nfl_games.sql')

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        
def drop_dfs_tables(config_in: configure_db.DFSdbConfig = configure_db.defaultDFSConfig()):
    try:
        db_interface = DFSDBInterface(config_in)

        commands = [
            "DROP TABLE IF EXISTS draftables",
            "DROP TABLE IF EXISTS competitions",
            "DROP TABLE IF EXISTS contests",
            "DROP TABLE IF EXISTS payouts",
            "DROP TABLE IF EXISTS player_game_stats",
            "DROP TABLE IF EXISTS projections"
        ]

        db_interface.run_commands(commands)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def clean_dfs_tables(config_in: configure_db.DFSdbConfig = configure_db.defaultDFSConfig()):
    drop_dfs_tables(config_in)
    create_dfs_tables(config_in)


def create_dfs_tables(config_in: configure_db.DFSdbConfig = configure_db.defaultDFSConfig()):
    """ create tables in the PostgreSQL database"""
    commands = [
        """
        CREATE TABLE IF NOT EXISTS draftables (
            id INTEGER PRIMARY KEY,
            team_id INTEGER NOT NULL,
            team_abbreviation   varchar(255) NOT NULL,
            player_id INTEGER NOT NULL,
            draft_group_id INTEGER NOT NULL,
            competition_id INTEGER,
            name VARCHAR(255) NOT NULL,
            position VARCHAR(255) NOT NULL,
            roster_slot_id INTEGER NOT NULL,
            salary DECIMAL,
            swappable BOOLEAN NOT NULL,
            disabled BOOLEAN NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS competitions (
            id INTEGER PRIMARY KEY,
            name varchar(255) NOT NULL,
            starts_at timestamp NOT NULL,
            week integer NOT NULL,
            home_team_id integer NOT NULL,
            home_team_name varchar(255) NOT NULL,
            home_team_abbreviation varchar(255) NOT NULL,
            home_team_city varchar(255) NOT NULL,
            away_team_id integer NOT NULL,
            away_team_name varchar(255) NOT NULL,
            away_team_abbreviation varchar(255) NOT NULL,
            away_team_city varchar(255) NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS players_dict
        (
             player_name         varchar(255),
             position            varchar(255),
             team                varchar(255),
             draftkings_name     varchar(255) NOT NULL,
             player_id           integer NOT NULL,
             PRIMARY KEY (player_name, position, team)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS competitions_dict
        (
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS contests
        (
             contest_id            int PRIMARY KEY,
             double_up             boolean NOT NULL,
             draft_group_id        int NOT NULL,
             fifty_fifty           boolean NOT NULL,
             guaranteed            boolean NOT NULL,
             head_to_head          boolean NOT NULL,
             name                  varchar(255) NOT NULL,
             payout                decimal NOT NULL,
             starred               boolean NOT NULL,
             starts_at             timestamp NOT NULL,
             week                  integer NOT NULL,
             entries_max           int NOT NULL,
             entries_fee           decimal NOT NULL,
             contest_type          int NOT NULL,
             games_count           int NOT NULL,
             multientry            int NOT NULL,
             max_entry_fee         decimal NOT NULL,
             rake                  decimal
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS payouts
        (
             contest_id     int NOT NULL,
             min_position   int NOT NULL,
             max_position   int NOT NULL,
             payout_cash    decimal NULL,
             payout_tickets varchar(255) NULL,
             PRIMARY KEY (contest_id, min_position)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS contest_entries
        (
            entry_id    bigint PRIMARY KEY,
            contest_id  int NOT NULL,
            week        int NOT NULL,
            draft_group_id  int NOT NULL,
            entry_name  varchar(255) NOT NULL,
            rank        int NOT NULL,
            points_total      decimal NOT NULL,
            gross_cash_winnings decimal NOT NULL
        );
        CREATE INDEX IF NOT EXISTS contest_entries_entry_id_idx ON contest_entries(entry_id);
        CREATE INDEX IF NOT EXISTS contest_entries_contest_id_idx ON contest_entries(contest_id);
        CREATE INDEX IF NOT EXISTS contest_entries_week_idx ON contest_entries(week);
        CREATE INDEX IF NOT EXISTS contest_entries_dgid_idx ON contest_entries(draft_group_id);
        CREATE INDEX IF NOT EXISTS contest_entries_entry_name_idx ON contest_entries(entry_name);
        """,
        """
        CREATE TABLE IF NOT EXISTS contest_rosters
        (
            week        int NOT NULL,
            draft_group_id  int NOT NULL,
            contest_id  int NOT NULL,
            entry_id    bigint NOT NULL,
            roster_slot_id  int NOT NULL,
            player_id int NOT NULL,
            salary      decimal,
            position    varchar(255),
            PRIMARY KEY (entry_id, player_id)
        );
        CREATE INDEX IF NOT EXISTS contest_rosters_entry_id_idx ON contest_rosters(entry_id);
        CREATE INDEX IF NOT EXISTS contest_rosters_week_idx ON contest_rosters(week);
        CREATE INDEX IF NOT EXISTS contest_rosters_dgid_idx ON contest_rosters(draft_group_id);
        CREATE INDEX IF NOT EXISTS contest_rosters_cid_idx ON contest_rosters(contest_id);
        CREATE INDEX IF NOT EXISTS contest_rosters_roster_slot_id_idx ON contest_rosters(roster_slot_id);
        CREATE INDEX IF NOT EXISTS contest_rosters_player_id_idx ON contest_rosters(player_id);
        """,
        """
        CREATE TABLE IF NOT EXISTS contest_entry_stats
        (
            entry_id    bigint PRIMARY KEY,
            contest_id  int NOT NULL,
            entry_name  varchar(255) NOT NULL,
            stack       varchar(255) NOT NULL,
            usage_by_position       varchar(255) NOT NULL,
            usage_by_roster_slot       varchar(255) NOT NULL,
            usage_total decimal NOT NULL,
            projection_total decimal NOT NULL,
            projection_by_position varchar(255) NOT NULL,
            projection_by_roster_slot varchar(255) NOT NULL,
            salary_total decimal NOT NULL,
            salary_by_position varchar(255) NOT NULL,
            salary_by_roster_slot varchar(255) NOT NULL
        );
        CREATE INDEX IF NOT EXISTS contest_entry_stats_entry_id_idx ON contest_entry_stats(entry_id);
        CREATE INDEX IF NOT EXISTS contest_entry_stats_contest_id_idx ON contest_entry_stats(contest_id);
        CREATE INDEX IF NOT EXISTS contest_entry_stats_entry_name_idx ON contest_entry_stats(entry_name);
        """,
        """
        CREATE TABLE IF NOT EXISTS player_game_stats
        (
             week        int NOT NULL,
             player_id   int NOT NULL,
             fpts_ppr    decimal NULL,
             PRIMARY KEY (week, player_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS projections
        (
             week           int NOT NULL,
             player_id      int NOT NULL,
             projection_ppr decimal NULL,
             sd_pts         decimal NULL,
             dropoff        decimal NULL,
             floor          decimal NULL,
             ceiling        decimal NULL,
             points_vor     decimal NULL,
             floor_vor      decimal NULL,
             ceiling_vor    decimal NULL,
             uncertainty    decimal NULL,
             PRIMARY KEY (week, player_id)
        );
        """
    ]
    try:
        db_interface = DFSDBInterface(config_in)
        db_interface.run_commands(commands)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


if __name__ == "__main__":
    clean_nfl_tables()
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-f", "--file", help=f"Path to database .ini file to use. Default: {configure_db.defaultDFSConfig().INI}", type=str, default=configure_db.defaultDFSConfig().INI)
    # parser.add_argument("-c", "--clean_db", action="store_true", help="Use to drop the database before building", default=False)
    # args = parser.parse_args()

    # db_file = args.file
    # clean_db = args.clean_db
    # configObj = configure_db.defaultDFSConfig()

    # if clean_db:
    #     clean_tables(configObj)
    # else:
    #     create_tables(configObj)
