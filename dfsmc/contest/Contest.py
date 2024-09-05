import pandas as pd
import numpy as np
import pathlib
from typing import List

from dfsdata.interface import DFSDBInterface
from dfsmc.projection import covariance


class Contest:

    contest_id = 0
    draft_group_id = 0

    def __init__(self, contest_id: int = None, db_interface: DFSDBInterface = None):
        self.contest_id = contest_id
        self.db_interface = db_interface
        self.populate_contest_data()

    def __str__(self):
        output_dict = {'id': self.contest_id, 'entries': self.entries_max, 'payout': self.payout}
        return str(output_dict)

    def populate_contest_data(self):
        query = "SELECT * FROM contests WHERE contest_id = %s"
        contest_data = self.db_interface.run_format_command(query, (self.contest_id,))
        contest_data = contest_data.to_dict('records')[0]
        for val in contest_data.keys():
            self.__setattr__(val, contest_data[val])

    def get_contests_with_same_draft_group(self):
        query = "SELECT * FROM contests WHERE draft_group_id = %s"
        contest_data = self.db_interface.run_format_command(query, (self.draft_group_id,))
        return contest_data

    def get_payouts(self):
        query = "SELECT * FROM payouts WHERE contest_id = %s"
        payout_data = self.db_interface.run_format_command(query, (self.contest_id, ))
        return Payout(payout_data)


class Payout:

    def __init__(self, payouts: pd.DataFrame):
        self.data = payouts


def field_filename(week: int, contest_id: int):
    return pathlib.Path(__file__).parent.parent.parent.resolve() / 'contest_entries' / '2023' / f'Week{week}' / f'lineups_{contest_id}.csv'


class MyString:

    """
    Helper class to allow matrix multiplication on vectors of strings, by concatenation
    """

    _value: str

    def __init__(self, string: str):
        self._value = string

    def __rmul__(self, other: float):
        if other > 0.:
            return self._value
        else:
            return ''

    def __str__(self):
        return self._value


class LineupSet:

    """
    fields:
    player_data: dataframe of draftables from Lineup.DraftGroup.  Must have a numerical index by which to filter lineups
    The standard lexicographic order is to sort the DraftGroup by player_id and roster_slot_id - this can be used to
    reset the index if necessary
    lineups: numpy 2d array where a row gives the indices of players in a given lineup and each row corresponds to one
    lineup.  If this is used to generate a sparse matrix, matrix multiplication can be used on the underlying array
    making up the player_data frame to sum attributes such as salary, projection, usage and score.
    """

    def __init__(self, player_data: pd.DataFrame, lineups: np.array, covariance_matrix=None):
        if lineups.shape[1] == len(player_data):
            # this means lineups is giving 1's and 0's, and was generated from another LineupSet
            self.lineups = lineups
        else:
            # this means lineups is giving a list of player indices, which must be converted to a sparse matrix
            self.lineups = np.zeros((len(lineups), len(player_data)))
            rows = np.indices((lineups.shape[0], )).reshape(-1, 1)
            self.lineups[rows, lineups] = 1

        # remove unused players (zero columns)
        players_used = np.any(self.lineups, axis=0)
        self.lineups = self.lineups[:, players_used]
        self.player_data = player_data.loc[players_used].copy()
        self.player_data['projection'] = self.player_data['projection'].astype(float)
        # self.player_data['covariance'] = self.player_data['covariance'].astype(float)
        self.cov = covariance_matrix[np.outer(players_used, players_used)].reshape(sum(players_used), sum(players_used))

    def lineup_set_overlap_matrix(self, row: np.array = None, subset: bool = False) -> np.ndarray:
        # covariance matrix for entire LineupSet is given by self.lineups @ self.cov @ self.lineups.T
        # If subset=True, return cov matrix only for given rows.  Otherwise return cov for all lineups
        if row is None:
            return self.lineups @ self.lineups.T
        if subset:
            return self.lineups[row, :] @ self.lineups[row, :].T
        return self.lineups[row, :] @ self.lineups.T

    def lineup_set_covariance_matrix(self, row: np.array = None, subset: bool = False) -> np.ndarray:
        # covariance matrix for entire LineupSet is given by self.lineups @ self.cov @ self.lineups.T
        # If subset=True, return cov matrix only for given rows.  Otherwise return cov for all lineups
        if row is None:
            return self.lineups @ self.cov @ self.lineups.T
        if subset:
            return self.lineups[row, :] @ self.cov @ self.lineups[row, :].T
        return self.lineups[row, :] @ self.cov @ self.lineups.T

    def lineup_set_diagonal_covariance(self):
        # to get the diagonal covariance of each lineup do sum_over_rows(self.lineups @ self.cov * self.lineups)
        player_cov = (self.lineups @ self.cov) * self.lineups
        cov_values = player_cov @ np.ones((player_cov.shape[1], 1))
        return cov_values

    def generate_max_coverage(self, n: int = 20) -> np.ndarray:
        """

        :param n: number of lineups
        """
        lineup_df = self.get_lineup_stats()
        remaining_cov = self.lineup_set_diagonal_covariance().flatten()
        idx = np.random.randint(low=0, high=len(remaining_cov))
        lineups = np.array([idx])
        for i in range(n-1):
            remaining_cov = np.sum(self.lineup_set_covariance_matrix(lineups), axis=0)
            remaining_cov[lineups] = np.max(remaining_cov)  # remove repeats from consideration
            idx = np.argmin(np.abs(remaining_cov))
            lineups = np.append(lineups, [idx])

        return lineups

    def get_lineup_stats(self) -> pd.DataFrame:
        value_cols = ['salary', 'projection', 'actual']
        lineup_values = self.lineups @ self.player_data[value_cols].values

        self.player_data['name_id'] = [MyString(f'{val[0]}:{str(val[1])}') for val in
                                         zip(self.player_data['name'].values, self.player_data['id'].values)]
        self.player_data['name_slot'] = [MyString(f'({val[0]}:{val[1]})') for val in
                                         zip(self.player_data['roster_slot'].values, self.player_data['name_id'].values)]
        name_values = self.lineups @ self.player_data['name_slot'].values

        cov_values = self.lineup_set_diagonal_covariance()

        # sort lineup strings to put CPT first
        def sort_lineup_string(lineup):
            players = np.sort([player.lstrip('(').rstrip(')') for player in lineup.split(')(')])
            return ''.join(['(' + playername + ')' for playername in players])

        f = np.vectorize(sort_lineup_string)
        name_values = f(name_values)

        file_array = np.concatenate((np.reshape(name_values, (-1, 1)), lineup_values, cov_values), axis=1)
        df = pd.DataFrame(file_array, columns=['lineup'] + value_cols + ['covariance'])
        df[value_cols + ['covariance']] = df[value_cols + ['covariance']].astype(float)
        return df.sort_values(by='covariance', ascending=False)

    def to_file(self, outfile: pathlib.Path):
        self.get_lineup_stats().to_csv(outfile)

    @staticmethod
    def convert_to_uploadable(infile: pathlib.Path, idx: List[int] = None):
        lineups = pd.read_csv(infile, index_col='Unnamed: 0')
        if idx is None:
            lineup_list = lineups['lineup'].values
        else:
            lineup_list = lineups.loc[idx, 'lineup'].values

        def get_name_and_id_list(lineup_string):
            players = lineup_string.split(')(')
            name_and_id = [player.split(':')[1:] for player in players]
            return [f'{name[0].lstrip("(")} ({name[1].rstrip(")")})' for name in name_and_id]

        header = ','.join([val.lstrip('(').split(':')[0] for val in lineup_list[0].split(')(')])
        names = [','.join(get_name_and_id_list(val)) for val in lineup_list]
        filename = infile.stem
        filedir = infile.parent
        outfile = filedir / (filename + '_upload.csv')
        with open(outfile, 'w') as file:
            file.write(header + ',\n')
            count = 0
            for lineup in names:
                if count < 500:
                    file.write(lineup + ',\n')
                    count += 1
                else:
                    print('Warning: Cannot upload more than 500 lineups with a single file!  Breaking')
                    break

        return outfile

    def filter(self, lineups: np.ndarray):
        return LineupSet(self.player_data, self.lineups[lineups], self.cov)


class Field(LineupSet):
    """
    The set of all lineups entered into a contest
    """

    def __init__(self, player_data: pd.DataFrame, lineups: np.array, covariance_matrix=None):
        super().__init__(player_data, lineups, covariance_matrix)


class ContestEntry(LineupSet):
    """
    Set of Lineups to enter into a contest
    """

    def __init__(self, player_data: pd.DataFrame, lineups: np.array, covariance_matrix=None):
        super().__init__(player_data, lineups, covariance_matrix)


if __name__ == "__main__":
    from dfsmc.lineup import Lineup

    contest = 164284870
    contest = Contest(contest_id=contest, db_interface=DFSDBInterface())

    constraint = Lineup.LineupConstraint(contest_type='Showdown')
    draft_group = Lineup.DraftGroup(draft_group_id=contest.draft_group_id, db_interface=DFSDBInterface())

    # Get player projection data
    draft_group.populate_points_data(DFSDBInterface())
    players = draft_group.data

    # Generate usage projections for this contest
    # usage_predictor = usage.UsagePredictor(usage.UsageModel.SIMPLE, draft_group.data)
    # players = usage_predictor.predict()

    # Generate all possible lineups
    generator = Lineup.greedyGenerator(constraint, players, projections_only=True)
    lineups = generator.generate(verbose=True, limit=None, random=False)

    # Get the covariance matrix
    cov_group = covariance.DraftGroupCovariance(players)
    cov_matrix = cov_group.get_covariance()

    field = LineupSet(players, lineups, cov_matrix)
    # field.generate_max_coverage()

    lineup_data = field.get_lineup_stats()

    indices = lineup_data[lineup_data['salary'] >= 49000.].index.values
    field_filtered = field.filter(indices)

    selection = field_filtered.generate_max_coverage(20)
    print('hello')