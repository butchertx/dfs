# import database.interface as db
# from contest import Contest
# from lineup import Lineup

# if __name__ == "__main__":
#     # Get DraftGroup from example contest
#     contest = Contest.Contest(contest_id=111403139, db_interface=db.DFSDBInterface())
#     draft_group = Lineup.DraftGroup(draft_group_id=contest.draft_group_id, db_interface=db.DFSDBInterface())

#     # get all contests using the same draft group
#     contest_data = contest.get_contests_with_same_draft_group()