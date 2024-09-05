import itertools
from typing import List
import pandas as pd
import numpy as np
from iteration_utilities import random_product


from dfsdata.interface import DFSDBInterface
from dfsmc.lineup import utils as l_utils

ROSTER_DICT = l_utils.DK_ROSTER_SLOTS

class Player:

    def __init__(self, player_id=None, name=None, team=None, position=None, roster_slot_id=None, salary=None, opponent=None):
        self.player_id = player_id
        self.name = name
        self.team = team
        self.position = position
        self.roster_slot_id = roster_slot_id
        try:
            self.roster_slot = ROSTER_DICT[str(roster_slot_id)]
        except KeyError:
            print(f'Uncategorized roster slot id: {roster_slot_id}')
        self.salary = salary
        self.opponent = opponent

        self.fantasy_points_projection = 0.0
        self.sd_pts = 0.0
        self.fantasy_points_actual = 0.0
        self.projection_data = None

    def __str__(self):
        return f'{self.name}:{self.roster_slot}:{self.team}:{self.salary}'

    def get_projection_fpros(self, week: int, db_interface: DFSDBInterface):
        print('Warning: Lineup.Player.get_projection_fpros is deprecated.  Use Lineup.Player.get_projection_data.')
        projections = db_interface.run_format_command(
            "SELECT fpros_projection FROM projections WHERE week = %s AND player_id = %s",
            (week, self.player_id)
        )
        try:
            # TODO: update this to include special contest captain types
            if self.roster_slot == 'CPT':
                return 1.5 * float(projections.loc[0, 'fpros_projection'])
            return float(projections.loc[0, 'fpros_projection'])
        except Exception as err:
            return None

    def get_projection_data(self, week: int, db_interface: DFSDBInterface):
        projections = db_interface.run_format_command(
            """SELECT *
                FROM projections WHERE week = %s AND player_id = %s
            """,
            (int(week), self.player_id)
        )
        points_cols = ['projection_ppr', 'sd_pts', 'dropoff', 'floor', 'ceiling', 'points_vor', 'floor_vor', 'ceiling_vor']

        try:
            # TODO: update this to include special contest captain types
            projections[points_cols] = projections[points_cols].astype(float)
            if self.roster_slot == 'CPT':
                return 1.5 * projections.loc[0, points_cols]
            return projections.loc[0, points_cols]
        except Exception as err:
            return None

    def get_points_data(self, week: int, db_interface: DFSDBInterface):
        points = db_interface.run_format_command(
            """SELECT *
                FROM player_game_stats WHERE week = %s AND player_id = %s
            """,
            (int(week), self.player_id)
        )
        points_cols = ['fpts_ppr']

        try:
            # TODO: update this to include special contest captain types
            points[points_cols] = points[points_cols].astype(float)
            if self.roster_slot == 'CPT':
                return 1.5 * points.loc[0, points_cols]
            return points.loc[0, points_cols]
        except Exception as err:
            return None

    def set_projection_fpros(self, week: int, db_interface: DFSDBInterface):
        print('Warning: Lineup.Player.set_projection_fpros is deprecated.  Use Lineup.Player.set_projection_data.')
        self.fantasy_points_projection = self.get_projection_fpros(week, db_interface)

    def set_projection_data(self, week: int, db_interface: DFSDBInterface):
        proj_data = self.get_projection_data(week, db_interface)
        if proj_data is not None:
            self.fantasy_points_projection = proj_data.projection_ppr
            self.sd_pts = proj_data.sd_pts
            self.projection_data = proj_data

    def set_points_data(self, week: int, db_interface: DFSDBInterface):
        points_data = self.get_points_data(week, db_interface)
        if points_data is not None:
            self.fantasy_points_actual = points_data.fpts_ppr


class Stack:

    def __init__(self, player_list: List[Player]):
        self.players = player_list  # list (set) of players
        self.valid = self.is_valid()
        self.fantasy_points_projection = self.sum_attrs('fantasy_points_projection')
        self.fantasy_points_actual = self.sum_attrs('fantasy_points_actual')
        self.covariance_matrix = None  # projected cov
        self.covariance = None  # sum all elements in cov matrix
        self.salary = self.sum_attrs('salary')

    def __str__(self):
        return '----\n' + '\n'.join([str(p) for p in self.players]) + '\n----'

    def is_valid(self):
        team = self.players[0].team
        valid = True
        for player in self.players:
            valid = valid and ((player.team == team) or (player.opponent == team))
        return valid

    def sum_attrs(self, attr: str):
        try:
            return sum([getattr(player, attr) for player in self.players])
        except AttributeError:
            raise AttributeError(f'Players in Stack do not have the {attr} attribute')


class LineupConstraint:

    def __init__(self, contest_type: str = 'Showdown'):
        if contest_type == 'Showdown':
            self.contest_type = 'Showdown'
            self.salary_max = 50000
            self.roster_counts = {'CPT': 1, 'FLEX': 5}
            self.unique_teams = 2
        else:
            raise NotImplementedError(f'LineupConstraint not implemented for {contest_type}')

    def is_valid(self, player_data: pd.DataFrame):
        """ Check if a Lineup is valid

        :param player_data: DataFrame with columns: name, salary, roster_slot
        :return: boolean.  True if list of players meets constraints
        """
        if sum(player_data['salary']) > self.salary_max:
            # print(f"Salary exceeds max: {sum(player_data['salary'])}")
            return False
        for slot in self.roster_counts.keys():
            if not len(player_data[player_data['roster_slot'] == slot]) == self.roster_counts[slot]:
                return False

        return True


class DraftGroup:

    def __init__(self, contest_id: int = None, draft_group_id: int = None, db_interface: DFSDBInterface = None):
        if contest_id is not None:
            self.data = self._get_data('contest', contest_id, db_interface)
        elif draft_group_id is not None:
            self.data = self._get_data('draft', draft_group_id, db_interface)
        else:
            raise Exception(
                "Either contest_id or draft_group_id must be specified "
                "with DB interface in LineupConstraint constructor")
        # Clean data types
        self.data['salary'] = self.data['salary'].astype(int)
        teams = self.data['team_abbreviation'].unique()
        if len(teams) > 2:
            raise NotImplementedError('Contests other than Showdown not implemented!')
        self.data['opponent'] = self.data['team_abbreviation']
        self.data.loc[self.data['team_abbreviation'] == teams[0], 'opponent'] = teams[1]
        self.data.loc[self.data['team_abbreviation'] == teams[1], 'opponent'] = teams[0]
        self.data['roster_slot'] = self.data['roster_slot_id'].astype(str).map(ROSTER_DICT)
        self.player_list = self._generate_players()

    def _get_data(self, query_type: str, id: int, db_interface: DFSDBInterface):
        if query_type == 'contest':
            query = "SELECT draftables.*, c.week, competitions.home_team_abbreviation, competitions.away_team_abbreviation FROM draftables " \
                    "INNER JOIN " \
                    "(SELECT draft_group_id, week FROM contests " \
                    "WHERE contests.contest_id = %s) as c " \
                    "ON c.draft_group_id = draftables.draft_group_id " \
                    "INNER JOIN competitions " \
                    "ON draftables.competition_id = competitions.id "
        elif query_type == 'draft':
            query = "SELECT draftables.*, c.week, competitions.home_team_abbreviation, competitions.away_team_abbreviation FROM draftables " \
                    "INNER JOIN " \
                    "(SELECT draft_group_id, week FROM contests " \
                    "WHERE contests.draft_group_id = %s LIMIT 1) as c " \
                    "ON c.draft_group_id = draftables.draft_group_id " \
                    "INNER JOIN competitions " \
                    "ON draftables.competition_id = competitions.id "
        else:
            raise NotImplementedError("Only contest_id and draft_group_id are implemented for DraftGroup init")

        return db_interface.run_format_command(query, (id,)).sort_values(
            by=['player_id', 'roster_slot_id']).reset_index().drop(columns='index')

    def _generate_players(self) -> List[Player]:
        result = []
        for item in self.data.itertuples():
            result.append(
                Player(
                    item.player_id,
                    item.name,
                    item.team_abbreviation,
                    item.position,
                    item.roster_slot_id,
                    item.salary,
                    item.opponent
                )
            )

        return result

    def populate_points_data(self, db_interface: DFSDBInterface):
        for p in self.player_list:
            p.set_projection_fpros(int(self.data.loc[0, 'week']), db_interface)
            # p.set_projection_data(int(self.data.loc[0, 'week']), db_interface)
            p.set_points_data(int(self.data.loc[0, 'week']), db_interface)
        mapping_proj = {(p.player_id, p.roster_slot_id): p.fantasy_points_projection for p in self.player_list}
        mapping_var = {(p.player_id, p.roster_slot_id): p.sd_pts ** 2 for p in self.player_list}
        mapping_points = {(p.player_id, p.roster_slot_id): p.fantasy_points_actual for p in self.player_list}
        self.data['projection'] = pd.Series(list(zip(self.data.player_id, self.data.roster_slot_id))).map(mapping_proj)
        self.data['variance'] = pd.Series(list(zip(self.data.player_id, self.data.roster_slot_id))).map(mapping_var)
        self.data['actual'] = pd.Series(list(zip(self.data.player_id, self.data.roster_slot_id))).map(mapping_points)
        
    def filter_by_projection(self, threshold: float = 1.0):
        cpt_filtered = self.data.loc[(self.data['projection'] > 1.5*threshold) & (self.data['roster_slot'] == 'CPT')].dropna()
        flex_filtered = self.data.loc[(self.data['projection'] > threshold) & (self.data['roster_slot'] == 'FLEX')].dropna()
        self.data = pd.concat([cpt_filtered, flex_filtered]).reset_index(drop='index')

    def populate_covariance(self):
        """
        Assumes projections have already been populated
        :return:
        """

    def exclude(self, exclude_list: List[int]):
        """
        Remove players with ids in exclude_list from the DraftGroup
        :param exclude_list:
        :return:
        """
        self.data = self.data[~(self.data['player_id'].isin(exclude_list))].reset_index().drop(columns='index')
        self.player_list = [p for p in self.player_list if p.player_id not in exclude_list]

    def __str__(self):
        output_dict = {'id': self.data.loc[0, 'draft_group_id'], 'player_count': len(self.data)}
        return str(output_dict)


class Lineup:

    attrs_to_sum = ['salary', 'fantasy_points_projection', 'fantasy_points_actual']

    def __init__(self, constraint: LineupConstraint, stacks: List[Stack] = None, lineup_data: pd.DataFrame = None):
        if constraint.contest_type == 'Showdown':
            # stack is just all players
            player_list = []
            for item in lineup_data.itertuples():
                player_list.append(Player(item.player_id, item.name, item.team_abbreviation, item.position, item.roster_slot_id, item.salary, item.opponent))

            self.stacks = [Stack(player_list)]
        else:
            raise NotImplementedError(f'Lineup not implemented for {constraint.contest_type}')

        # Builder
        self.constraint = constraint
        self.salary = self.sum_attrs('salary')

        # Check validity

        # Aggregate stats'
        self.fantasy_points_projection = self.sum_attrs('fantasy_points_projection')
        self.fantasy_points_actual = self.sum_attrs('fantasy_points_actual')

    def __str__(self):
        return f'Salary: {self.salary}\n================\n' + '\n'.join([str(s) for s in self.stacks])

    def is_valid(self):
        pass

    def sum_attrs(self, attr: str):
        try:
            return sum([getattr(stack, attr) for stack in self.stacks])
        except AttributeError:
            raise AttributeError(f'Stacks in Lineup do not have the {attr} attribute')


class randomLineupGenerator:

    def __init__(self, constraint: LineupConstraint, player_data: pd.DataFrame):
        """

        :param constraint (LineupConstraint): constraint for determining lineup validity
        :param player_data (pd.DataFrame): assumes columns: player, roster_slot_id, salary, usage, others depending on subclass
        """
        self.rng = np.random.Generator(np.random.PCG64())
        self.constraint = constraint
        self.player_data = player_data
        self.player_data['num_roster_slots'] = self.player_data['roster_slot'].map(self.constraint.roster_counts)
        # self.usage_is_valid = self._usage_valid()

    def _usage_valid(self):
        """
        Not current used
        :return:
        """
        self.player_data['salary_density'] = self.player_data['num_roster_slots'] * self.player_data['salary'] * self.player_data['usage_pct']
        return sum(self.player_data['salary_density']) < self.constraint.salary_max


class independentUsageGenerator(randomLineupGenerator):

    """
    Not currently used
    """

    roster_slot_order = ['CPT', 'FLEX']

    def __init__(self, constraint: LineupConstraint, player_data: pd.DataFrame, num_lineups: int):
        super().__init__(constraint, player_data)
        self.num_lineups = num_lineups

    def generate(self, verbose=False):
        lineups = []
        players_probs = {roster_slot: self.player_data.loc[self.player_data['roster_slot'] == roster_slot, ['name', 'usage_pct']].copy() for roster_slot in self.roster_slot_order}
        slot_results = {}
        # TODO: Parallelize.  Doesn't look like there's a built-in way to do this
        while len(lineups) < self.num_lineups:
            for slot in self.roster_slot_order:
                slot_results[slot] = self.rng.choice(players_probs[slot].index.values, size=self.constraint.roster_counts[slot], replace=False, p=players_probs[slot]['usage_pct'], shuffle=False)

            lineup_list = np.array([elem for sublist in slot_results.values() for elem in sublist])
            lineup = self.player_data.loc[lineup_list][['name', 'roster_slot', 'salary']]
            if self.constraint.is_valid(lineup):
                lineups.append(Lineup(self.constraint, lineup_data=self.player_data.loc[lineup_list]))
                if verbose:
                    print(f'{len(lineups)} of {self.num_lineups} generated.')

        return np.array(lineups)


class RandomProduct:

    """
    Use random_product from random_utilities.
    TODO: Might need to look into setting random.seed
    """

    def __init__(self, inputs, limit=None):
        self.inputs = inputs
        self.input_size = len(inputs)
        if limit is not None:
            self.samples = random_product(*inputs, repeat=limit)
        else:
            self.samples = random_product(*inputs)
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        result = self.samples[self.index:self.index+self.input_size]
        self.index += self.input_size
        if self.index == len(self.samples):
            raise StopIteration
        return result


class greedyGenerator(randomLineupGenerator):
    """
    Generate all valid, viable lineups for a showdown
    valid: doesn't go over salary cap or have repeat players
    viable: all players have a nonzero projection
    """

    roster_slot_order = ['CPT', 'FLEX']
    _projections_only: bool  # use only players that have a projection

    def __init__(self, constraint: LineupConstraint, player_data: pd.DataFrame, projections_only: bool = False):
        super().__init__(constraint, player_data)
        self._projections_only = projections_only
        if self._projections_only:
            player_data = player_data[~player_data['projection'].isna()]

    def generate(self, verbose=False, limit=None, random=False):
        """
        Generate all lineups using itertools.combinations() and itertools.product()

        Warning: using random=True with limit=None will lead to an infinite loop
        """
        lineups = []
        players = {roster_slot: self.player_data.loc[
            (self.player_data['roster_slot'] == roster_slot) & (self.player_data['projection'] > 0),
                                        'name'
                                    ].copy()
                   for roster_slot in self.roster_slot_order}
        slot_results = []
        # TODO: Parallelize.  Doesn't look like there's a built-in way to do this
        for slot in self.roster_slot_order:
            slot_results.append(itertools.combinations(players[slot].index.values, r=self.constraint.roster_counts[slot]))

        product_entries = [list(elem) for elem in slot_results]
        if random:
            lineup_iterator = iter(RandomProduct(product_entries, limit=limit))
        else:
            lineup_iterator = itertools.product(*product_entries)
        salaries = np.array(self.player_data['salary'].values)
        names = np.array(self.player_data['name'].values)
        teams = np.array(self.player_data['team_id'].values)
        while True:
            try:
                lineup = next(lineup_iterator)
                lineup = self._unroll_lineup(lineup)
                if len(set(teams[lineup])) == 2 and len(set(names[lineup])) == 6 and np.sum(salaries[lineup]) < self.constraint.salary_max:
                    lineups.append(lineup.T)
                    if verbose and len(lineups) % 10000 == 0:
                        print(f'{len(lineups)} lineups generated.')
                    if limit is not None and len(lineups) == limit:
                        break
            except StopIteration:
                break

        return np.vstack(lineups)

    def _unroll_lineup(self, lineup):
        return np.array([elem for sublist in lineup for elem in sublist])
