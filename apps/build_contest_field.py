import pathlib
from typing import List

import dfsdata.interface as db
from dfsmc.contest import Contest
from dfsmc.lineup import Lineup
# from dfsmc.projection import covariance
# from dfsmc.projection import usage


def build_field(contest_in: Contest, exclude_players: List[int] = None, projection_threshold: float = 1.0):
    # Get lineup parameters for contest
    constraint = Lineup.LineupConstraint(contest_type='Showdown')
    draft_group = Lineup.DraftGroup(draft_group_id=contest_in.draft_group_id, db_interface=db.DFSDBInterface())
    if exclude_players is not None:
        draft_group.exclude(exclude_players)

    # Get player projection data
    draft_group.populate_points_data(db.DFSDBInterface())
    draft_group.filter_by_projection(projection_threshold)

    # # Generate usage projections for this contest
    # usage_predictor = usage.UsagePredictor(usage.UsageModel.SIMPLE, draft_group.data)
    # players = usage_predictor.predict()

    # Generate all possible lineups
    generator = Lineup.greedyGenerator(constraint, draft_group.data, projections_only=True)
    lineups = generator.generate(verbose=True, limit=None, random=False)

    # # Get the covariance matrix
    # cov_group = covariance.DraftGroupCovariance(players)
    # cov_matrix = cov_group.get_covariance()

    # Build the Field using all valid and viable lineups for this contest
    # We want to do this so we can plot / calculate summary stats and compare to smaller subsets of maximal field
    return Contest.LineupSet(draft_group.data, lineups)


def build_lineup(contest_in: Contest):
    pass


def evaluate_lineup(field: Contest.LineupSet, lineup: Lineup.Lineup):
    pass


if __name__ == "__main__":

    exclude_players = None
    filename_suffix = None

    print("Welcome to the Lineup Builder")
    GEN_FIELD = True
    GEN_UPLOADS = False
    TO_FILE = True

    # Fill list with idx values corresponding to lineups output by the GEN_FIELD script
    contest_and_lineups = {
        164284870: []
    }

    # exclude_players = [
    #     728169
    # ]

    # filename_suffix = ''

    if GEN_FIELD:

        for key in contest_and_lineups.keys():
            # Get Contest data
            contest = Contest.Contest(contest_id=key, db_interface=db.DFSDBInterface())

            # generate a field
            field = build_field(contest, exclude_players=exclude_players)
            filepath = Contest.field_filename(contest.week, key)
            if filename_suffix is not None:
                filepath = pathlib.Path((filename_suffix + '.').join(str(filepath).split('.')))
            if TO_FILE:
                field.to_file(filepath)

    if GEN_UPLOADS:

        # Generate uploadable lineups
        for key, value in contest_and_lineups.items():
            contest = Contest.Contest(contest_id=key, db_interface=db.DFSDBInterface())
            filepath = Contest.field_filename(contest.week, key)
            if filename_suffix is not None:
                filepath = pathlib.Path((filename_suffix + '.').join(str(filepath).split('.')))
            if TO_FILE:
                Contest.LineupSet.convert_to_uploadable(filepath, value)





