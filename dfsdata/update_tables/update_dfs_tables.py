import json
import dateutil.parser

import pandas as pd
from fuzzywuzzy import process

from dfsdata.interface import DFSDBInterface
from dfsdata.path_name import ContestDataNames
from dfsdata import configure_db, path_name, dk_utils as dk


class DataWrangler:

    _db: DFSDBInterface
    _dk_names: ContestDataNames

    def __init__(self, db: DFSDBInterface):
        self._db = db
        self._dk_names = ContestDataNames(db.db_config)

    @property
    def db(self):
        return self._db

    @property
    def dk_names(self):
        return self._dk_names

    def read_contest_data(self):
        # read tables to get list of contest ids
        # filter out Madden streams, duplicates, and contests that don't have a details file
        contest_table_files = self.dk_names.contest_table_files()
        contest_table = pd.concat([pd.read_csv(f) for f in contest_table_files]).drop_duplicates(
            subset='contest_id')
        contest_table = contest_table.loc[
            (contest_table['contest_type'] != 'Madden Stream') & contest_table['guaranteed']]

        # get list of details files and drop extras from contest table
        detail_files = self.dk_names.contest_details_files()
        detail_file_dict = {self.dk_names.filename_to_id(filename): str(filename) for filename in detail_files}
        contest_table['detail_file'] = contest_table['contest_id'].map(detail_file_dict)
        contest_table = contest_table.dropna()

        # get list of already-indexed contests
        contests_indexed = self.db.run_command('SELECT contest_id FROM contests')
        try:
            contests_indexed_list = [int(c[0]) for c in contests_indexed]
        except ValueError: # no contests in database
            contests_indexed_list = []
        return contest_table[~contest_table['contest_id'].isin(contests_indexed_list)]

    def insert_contest_data(self, contest_table: pd.DataFrame):
        if len(contest_table) > 0:
            contest_command = """INSERT into contests (
                contest_id, double_up, draft_group_id, fifty_fifty, guaranteed, head_to_head, name,
                payout, starred, starts_at, week, entries_max, entries_fee, contest_type, games_count,
                multientry, max_entry_fee, rake )
                values %s
                ON CONFLICT DO NOTHING
                """

            # add week column
            contest_table['week'] = [dk.get_nfl_week(self.db.db_config.YEAR, int(dateutil.parser.isoparse(cstart).timestamp()))
                                     for cstart in contest_table['starts_at']]

            # read detail files and get multientry and max_entry_fee
            multientry_dict = {}
            for cid, filename in zip(contest_table['contest_id'], contest_table['detail_file']):
                f = open(filename)
                file_data = json.load(f)
                multientry_dict[cid] = file_data['contestDetail']['maximumEntriesPerUser']

            contest_table['multientry'] = contest_table['contest_id'].map(multientry_dict)
            contest_table['max_entry_fee'] = contest_table['multientry'] * contest_table['entries_fee']

            def rake(efee, emax, payout):
                if efee == 0 or emax == 999999999:
                    return 100
                decimal = 100. * (1.0 - payout / emax / efee)
                return decimal
            contest_table['rake'] = contest_table.apply(lambda x: rake(x['entries_fee'], x['entries_maximum'], x['payout']), axis=1)

            # Prepare and insert contest data
            contest_table = contest_table[['contest_id', 'double_up', 'draft_group_id', 'fifty_fifty',
                                           'guaranteed', 'head_to_head', 'name', 'payout', 'starred',
                                           'starts_at', 'week', 'entries_maximum', 'entries_fee', 'contest_type_id',
                                           'games_count', 'multientry', 'max_entry_fee', 'rake']]
            data_to_insert = [tuple(row.values.tolist()) for idx, row in contest_table.iterrows()]
            self.db.run_format_insert(contest_command, data_to_insert)

    def insert_contests_2023(self):
        print('Inserting contests...')
        contest_data = self.read_contest_data()
        self.insert_contest_data(contest_data)
    
    def insert_contests_2024(self):
        print('Inserting contests...')
        contest_data = self.read_contest_data()
        self.insert_contest_data(contest_data)

    def insert_draftables(self):
        # list files to be added
        files_existing = self.dk_names.draft_group_files()
        draft_groups_indexed = self.db.run_command('SELECT DISTINCT draft_group_id FROM draftables')
        if draft_groups_indexed is None:
            draft_groups_indexed_list = []
        else:
            draft_groups_indexed_list = [c[0] for c in draft_groups_indexed]
        files_to_add = [file for file in files_existing if self.dk_names.filename_to_id(file) not in draft_groups_indexed_list]

        if len(files_to_add) > 0:
            print('Inserting draftables...')
            # loop data files and accumulate in a list of tuples
            # insert draft group data one file at a time
            command = """INSERT into draftables (
                id, team_id, team_abbreviation, player_id, draft_group_id, competition_id, name, position,
                roster_slot_id, salary, swappable, disabled )
                values %s
                ON CONFLICT DO NOTHING
            """
            comp_command = """INSERT INTO competitions (
                id, name, starts_at, week, home_team_id, home_team_name, home_team_abbreviation, home_team_city,
                away_team_id, away_team_name, away_team_abbreviation, away_team_city )
                VALUES %s
                ON CONFLICT DO NOTHING
            """
            competitions_dict = {}

            for file in files_to_add:
                dgid = self.dk_names.filename_to_id(file)
                with open(file, 'r') as f:
                    file_data = json.load(f)
                players = file_data['draftables']
                competitions = file_data['competitions']
                data = [(
                    player['id'], player['team_id'], player['team_abbreviation'], player['player_id'], dgid,
                    player['competition']['id'], player['names']['display'].strip(), player['position'],
                    player['roster_slot_id'], player['salary'], player['swappable'], player['disabled']
                ) for player in players if player['competition'] is not None]
                self.db.run_format_insert(command, data)

                for c in competitions:
                    if c['id'] not in competitions_dict.keys():
                        home = c['home_team']
                        away = c['away_team']
                        gametime = int(dateutil.parser.isoparse(c['starts_at']).timestamp())
                        competitions_dict[c['id']] = (c['name'], c['starts_at'],
                                                      dk.get_nfl_week(self.db.db_config.YEAR, gametime),
                                                      home['id'], home['name'], home['abbreviation'], home['city'],
                                                      away['id'], away['name'], away['abbreviation'], away['city'])

            # update competitions list
            comp_data = [(ckey,) + competitions_dict[ckey] for ckey in competitions_dict.keys()]
            self.db.run_format_insert(comp_command, comp_data)

    def insert_payouts(self):
        print("Inserting payout stats...")
        # get files to add
        files_existing = self.dk_names.contest_details_files()
        contests_indexed = self.db.run_command('SELECT DISTINCT contest_id FROM payouts')
        contests_indexed_list = [c[0] for c in contests_indexed]
        files_to_add = [file for file in files_existing if self.dk_names.filename_to_id(file) not in contests_indexed_list]
        cid_to_add = [self.dk_names.filename_to_id(file) for file in files_to_add]

        # load files into a list
        all_payouts_loaded = []
        for cid, file in zip(cid_to_add, files_to_add):
            with open(file) as json_file:
                file_contents = json.load(json_file)
                all_payouts_loaded.append((cid, file_contents['contestDetail']['payoutSummary']))

        ins_data = []
        for payout in all_payouts_loaded:
            # payout is a dict with contest_id: list of payouts
            # append each row of this list to ins_data for the database table
            payout_flat = []
            for p in payout[1]:
                if 'Cash' in p['tierPayoutDescriptions'].keys():
                    cash = dk.get_cash_from_str(p['tierPayoutDescriptions']['Cash'])
                else:
                    cash = 0
                if 'Ticket' in p['tierPayoutDescriptions'].keys():
                    ticket = p['tierPayoutDescriptions']['Ticket']
                else:
                    ticket = ''

                temp_payout = (p['minPosition'], p['maxPosition'], cash, ticket)
                payout_flat.append(temp_payout)

            ins_data = ins_data + [(payout[0],) + places for places in payout_flat]

        ins_command = '''INSERT INTO payouts(
                        contest_id, min_position, max_position, payout_cash, payout_tickets
                        ) VALUES %s ON CONFLICT DO NOTHING'''
        self.db.run_format_insert(ins_command, ins_data)

    def match_player_names(self, player_pos_team: pd.DataFrame = None):
        """Check players_dict for matches to dk player_id

        for players in player_pos_team but not in players_dict, we want to
        find the matching draftkings name and player_id

        :param player_pos_team (pd.DataFrame): columns: ['Player', 'Pos', 'Team'].  List of players to match
        :return: None
        """
        if player_pos_team is None:
            print('Must provide list of players to match!')
            return

        # get dk players
        players_dk = self.db.run_command('SELECT DISTINCT player_id, name, position, team_abbreviation FROM draftables')
        players_dk = players_dk.rename(columns={'name': 'Player', 'position': 'Pos', 'team_abbreviation': 'Team'})

        insert_command = """INSERT INTO players_dict (
                    player_name, position, team, draftkings_name, player_id)
                    VALUES %s
                    ON CONFLICT DO NOTHING
                    """
        for idx, player_row in player_pos_team.iterrows():
            # get matches from players_dict.  If players_dict does not already have an entry, continue
            player_table = self.db.run_format_command('SELECT * FROM players_dict WHERE player_name = %s AND position = %s AND team = %s', (player_row['Player'], player_row['Pos'], player_row['Team']))
            if len(player_table) == 0:
                # if player already matches a DK player, add the player_id to players_dict
                match_rows = players_dk.loc[(players_dk['Player'] == player_row['Player'])
                                            & (players_dk['Pos'] == player_row['Pos'])].reset_index()
                if len(match_rows) >= 1:
                    ins_data = [tuple(player_row.values.tolist()) + (match_rows.at[0, 'Player'], str(match_rows.at[0, 'player_id']))]
                    self.db.run_format_insert(insert_command, ins_data)
                else:
                    # if player does not match a DK player, display nearest matches and allow user to enter a player_id
                    # if player is a defense, match the last word in their name
                    if player_row['Pos'] == 'DST':
                        dk_name = player_row['Player'].split()[-1]
                        dk_id = players_dk.loc[players_dk['Player'] == dk_name, 'player_id']
                        if len(dk_id) > 0:
                            match_id = str(dk_id.iloc[0])
                        else:
                            match_id = '0'
                    else:
                        print('Matching for player:')
                        print(player_row.values)
                        matches = process.extract(player_row['Player'], players_dk['Player'].values, limit=5)
                        match_display = players_dk[players_dk['Player'].isin([player[0] for player in matches])]
                        print('Potential matches:')
                        print(match_display[:])
                        match_id = input('Enter the matching player id (Enter 0 if no match):')

                    if not(match_id == '0'):
                        dk_player = self.db.run_format_command('SELECT player_id, name FROM draftables WHERE player_id = %s LIMIT 1', (match_id, ))
                        ins_data = [tuple(player_row.values.tolist()) + (dk_player.loc[0, 'name'], int(dk_player.loc[0, 'player_id']))]
                        self.db.run_format_insert(insert_command, ins_data)
                        print('Match successful!')
                    else:
                        ins_data = [tuple(player_row.values.tolist()) + ('', 0)]
                        self.db.run_format_insert(insert_command, ins_data)
                        print('No match found!')

    def match_player_names_2023(self):
        print('Matching player names...')

        # get fantasypros player names
        # fp_files = self.dk_names.fantasypros_files()
        # players_fp = dk.read_fantasy_pros_projections(list(fp_files)).drop_duplicates(
        #     subset=['Player', 'Pos', 'Team'])[['Player', 'Pos', 'Team']]
        # self.match_player_names(players_fp)

        # ffanalytics player names
        ff_files = self.dk_names.ffanalytics_files()
        players_ff = dk.read_ffanalytics_projections(list(ff_files)).drop_duplicates(
            subset=['Player', 'Pos', 'Team'])[['Player', 'Pos', 'Team']]
        self.match_player_names(players_ff)

        # stathead player names
        file = self.dk_names.player_game_file(2023)
        player_games = dk.read_player_games(file).drop_duplicates(subset=['Player', 'Pos', 'Team'])[['Player', 'Pos', 'Team']]
        self.match_player_names(player_games)
        
    def match_player_names_2024(self):
        print('Matching player names...')

        # get fantasypros player names
        fp_files = self.dk_names.fpros_files()
        players_fp = dk.read_fantasy_pros_projections(list(fp_files)).drop_duplicates(
            subset=['Player', 'Pos', 'Team'])[['Player', 'Pos', 'Team']]
        self.match_player_names(players_fp)

        # # ffanalytics player names
        # ff_files = self.dk_names.ffanalytics_files()
        # players_ff = dk.read_ffanalytics_projections(list(ff_files)).drop_duplicates(
        #     subset=['Player', 'Pos', 'Team'])[['Player', 'Pos', 'Team']]
        # self.match_player_names(players_ff)

        # # stathead player names
        # file = self.dk_names.player_game_file(2023)
        # player_games = dk.read_player_games(file).drop_duplicates(subset=['Player', 'Pos', 'Team'])[['Player', 'Pos', 'Team']]
        # self.match_player_names(player_games)
        
        # nfl.com player names

    def insert_fpros_projections(self):
        fp_files = self.dk_names.fpros_files()
        players_fp = dk.read_fantasy_pros_projections(list(fp_files))[['Player', 'Pos', 'Team', 'week', 'fpros_projection']]
        player_df = self.db.run_command('SELECT * from players_dict').rename(columns={'player_name': 'Player', 'position': 'Pos', 'team': 'Team'})
        points_fp = players_fp.merge(player_df, how='left', on=['Player', 'Pos', 'Team'])[[
            'Player', 'Pos', 'Team', 'player_id', 'week', 'fpros_projection']]
        points_fp['player_id'] = points_fp['player_id'].astype(int)
        points_fp = points_fp[points_fp['player_id'] != 0]
        points_fp = points_fp.drop(columns=['Player', 'Pos', 'Team'])

        data_to_insert = [tuple(row.values.tolist()) for idx, row in points_fp.iterrows()]
        ins_command = '''INSERT INTO projections(
                        player_id, week, fpros_projection
                        ) VALUES %s
                        ON CONFLICT ON CONSTRAINT projections_pkey
                        DO UPDATE SET fpros_projection = EXCLUDED.fpros_projection'''
        self.db.run_format_insert(ins_command, data_to_insert)

    def insert_ffanalytics_projections(self):
        ff_files = self.dk_names.ffanalytics_files()
        player_ffa = dk.read_ffanalytics_projections(list(ff_files))
        player_df = self.db.run_command('SELECT * from players_dict').rename(columns={'player_name': 'Player', 'position': 'Pos', 'team': 'Team'})
        points_ffa = player_ffa.merge(player_df, how='left', on=['Player', 'Pos', 'Team'])
        points_ffa['player_id'] = points_ffa['player_id'].astype(int)
        points_ffa = points_ffa[points_ffa['player_id'] != 0]
        points_ffa = points_ffa.drop(columns=['Player', 'Pos', 'Team'])[['week', 'player_id', 'projection_ppr', 'sd_pts', 'dropoff', 'floor', 'ceiling', 'points_vor', 'floor_vor', 'ceiling_vor', 'uncertainty']].drop_duplicates(subset=['week', 'player_id'])

        data_to_insert = [tuple(row.values.tolist()) for idx, row in points_ffa.iterrows()]
        ins_command = '''INSERT INTO projections(
                        week, player_id, projection_ppr, sd_pts, dropoff, floor, ceiling, points_vor, floor_vor, ceiling_vor, uncertainty
                        ) VALUES %s
                        ON CONFLICT ON CONSTRAINT projections_pkey
                        DO UPDATE SET projection_ppr = EXCLUDED.projection_ppr
                        '''
        '''
        DO UPDATE SET sd_pts = EXCLUDED.sd_pts
        DO UPDATE SET dropoff = EXCLUDED.dropoff
        DO UPDATE SET floor = EXCLUDED.floor
        DO UPDATE SET ceiling = EXCLUDED.ceiling
        DO UPDATE SET points_vor = EXCLUDED.points_vor
        DO UPDATE SET floor_vor = EXCLUDED.floor_vor
        DO UPDATE SET ceiling_vor = EXCLUDED.ceiling_vor
        DO UPDATE SET uncertainty = EXCLUDED.uncertainty
        '''
        self.db.run_format_insert(ins_command, data_to_insert)

    def insert_player_results_2023(self):
        file = self.dk_names.player_game_file(2023)
        player_games = dk.read_player_games(file)
        player_df = self.db.run_command('SELECT * from players_dict').rename(
            columns={'player_name': 'Player', 'position': 'Pos', 'team': 'Team'})
        player_games = player_games.merge(player_df, how='left', on=['Player', 'Pos', 'Team'])
        player_games['player_id'] = player_games['player_id'].astype(int)
        player_games = player_games[player_games['player_id'] != 0]
        player_games = player_games[['Week', 'player_id', 'fpts_ppr']].rename(columns={'Week': 'week'})

        data_to_insert = [tuple(row.values.tolist()) for idx, row in player_games.iterrows()]
        ins_command = '''INSERT INTO player_game_stats(
                                week, player_id, fpts_ppr
                                ) VALUES %s
                                ON CONFLICT ON CONSTRAINT player_game_stats_pkey
                                DO UPDATE SET fpts_ppr = EXCLUDED.fpts_ppr
                                '''
        self.db.run_format_insert(ins_command, data_to_insert)