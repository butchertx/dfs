import dfsdata.interface as db
from dfsmc.contest import Contest
from dfsmc.lineup import Lineup

if __name__ == "__main__":
    # Get DraftGroup from example contest
    contest = Contest.Contest(contest_id=164284870, db_interface=db.DFSDBInterface())
    draft_group = Lineup.DraftGroup(draft_group_id=contest.draft_group_id, db_interface=db.DFSDBInterface())

    # get all contests using the same draft group
    contest_data = contest.get_contests_with_same_draft_group()
    
    print(contest_data)