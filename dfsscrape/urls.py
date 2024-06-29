
"""
NCAAMBB TOURNEY
"""
# all since 1985
NCAAM_MM_FIRST4_85_TO_24 = "https://stathead.com/basketball/cbb/team-game-finder.cgi?request=1&timeframe=seasons&year_min=1985&comp_type=ncaat&tourn_id=f4&comp_id=NCAAM"
NCAAM_MM_64_85_TO_24 = "https://stathead.com/basketball/cbb/team-game-finder.cgi?request=1&timeframe=seasons&year_min=1985&comp_type=ncaat&tourn_id=r64&comp_id=NCAAM"
NCAAM_MM_32_85_TO_24 = "https://stathead.com/basketball/cbb/team-game-finder.cgi?request=1&timeframe=seasons&year_min=1985&comp_type=ncaat&tourn_id=r32&comp_id=NCAAM"
NCAAM_MM_REGIONAL_85_TO_24 = "https://stathead.com/basketball/cbb/team-game-finder.cgi?request=1&timeframe=seasons&year_min=1985&comp_type=ncaat&tourn_id=reg&comp_id=NCAAM"
NCAAM_MM_FINAL4_85_TO_24 = "https://stathead.com/basketball/cbb/team-game-finder.cgi?request=1&timeframe=seasons&year_min=1985&comp_type=ncaat&tourn_id=ff&comp_id=NCAAM"

"""
NCAAMBB REG SEASON
"""
def NCAAM_REG_SEASON_TEAM_PTS(year: str):
    return f"https://stathead.com/basketball/cbb/team-game-finder.cgi?request=1&timeframe=seasons&year_min={year}&year_max={year}&comp_type=reg&comp_id=NCAAM"

def NCAAM_REG_SEASON_TEAM_STATS(year: str):
    return f"https://stathead.com/basketball/cbb/team-game-finder.cgi?request=1&order_by_asc=1&order_by=team_name_abbr&timeframe=seasons&year_min={year}&year_max={year}&comp_type=reg&comp_id=NCAAM&ccomp%5B1%5D=gt&cstat%5B1%5D=orb&ccomp%5B2%5D=gt&cstat%5B2%5D=ast"

def NCAAM_REG_SEASON_TEAM_ADVANCED(year: str):
    return f"https://stathead.com/basketball/cbb/team-game-finder.cgi?request=1&order_by_asc=1&order_by=team_name_abbr&timeframe=seasons&year_min={year}&year_max={year}&comp_type=reg&comp_id=NCAAM&ccomp%5B4%5D=gt&cstat%5B4%5D=team_orb_pct&ccomp%5B5%5D=gt&cstat%5B5%5D=team_ast_pct&ccomp%5B6%5D=gt&cstat%5B6%5D=team_off_rtg"

"""
NFL Player Games
reg season and playoffs
"""
def NFL_PLAYER_GAMES_OFFENSE_ST(year: str):
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by=age_on_day&timeframe=seasons&year_min={year}&year_max={year}&comp_type=E&ccomp%5B1%5D=gt&cstat%5B1%5D=pass_cmp&ccomp%5B2%5D=gt&cstat%5B2%5D=rush_att&ccomp%5B3%5D=gt&cstat%5B3%5D=targets&ccomp%5B4%5D=gt&cstat%5B4%5D=all_td&ccomp%5B5%5D=gt&cstat%5B5%5D=fantasy_points&ccomp%5B6%5D=gt&cstat%5B6%5D=kick_ret&ccomp%5B7%5D=gt&cstat%5B7%5D=punt_ret"

def NFL_PLAYER_GAMES_DEFENSE_PUNTING(year: str):
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by=age_on_day&timeframe=seasons&year_min={year}&year_max={year}&comp_type=E&ccomp%5B8%5D=gt&cstat%5B8%5D=sacks&ccomp%5B9%5D=gt&cstat%5B9%5D=def_int&ccomp%5B10%5D=gt&cstat%5B10%5D=fumbles&ccomp%5B11%5D=gt&cstat%5B11%5D=punt"

def NFL_PLAYER_GAMES_TOUCHES(year: str):
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by=age_on_day&timeframe=seasons&year_min={year}&year_max={year}&comp_type=E&ccomp%5B10%5D=gt&cstat%5B10%5D=touches"

def NFL_PLAYER_GAMES_PASSING_(year: str):
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by=age_on_day&timeframe=seasons&year_min={year}&year_max={year}&comp_type=E&ccomp%5B2%5D=gt&cstat%5B2%5D=pass_target_yds&ccomp%5B3%5D=gt&cstat%5B3%5D=pass_batted_passes&ccomp%5B4%5D=gt&cstat%5B4%5D=pocket_time&ccomp%5B5%5D=gt&cstat%5B5%5D=pass_rpo"

def NFL_PLAYER_GAMES_SKILL_OFFENSE(year: str):
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by=age_on_day&timeframe=seasons&year_min={year}&year_max={year}&comp_type=E&ccomp%5B5%5D=gt&cstat%5B5%5D=rec_air_yds&ccomp%5B6%5D=gt&cstat%5B6%5D=rush_yds_before_contact"

def NFL_PLAYER_GAMES_ADVANCED_DEFENSE(year: str):
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by=age_on_day&timeframe=seasons&year_min={year}&year_max={year}&comp_type=E&ccomp%5B3%5D=gt&cstat%5B3%5D=def_targets"

def NFL_PLAYER_GAMES_SNAP_COUNTS(year: str):
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by=age_on_day&timeframe=seasons&year_min={year}&year_max={year}&comp_type=E&ccomp%5B1%5D=gt&cstat%5B1%5D=snaps_offense"

"""
Refactored URLs with stats filters
"""
def NFL_PLAYER_GAMES_PASSING(year: str):
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by=age_on_day&timeframe=seasons&year_min={year}&year_max={year}&comp_type=E&ccomp%5B8%5D=gt&cval%5B8%5D=1&cstat%5B8%5D=pass_att&ccomp%5B9%5D=gt&cstat%5B9%5D=rush_att&ccomp%5B11%5D=gt&cstat%5B11%5D=two_pt_md&ccomp%5B12%5D=gt&cstat%5B12%5D=fumbles&ccomp%5B13%5D=gt&cstat%5B13%5D=pass_target_yds&ccomp%5B14%5D=gt&cstat%5B14%5D=pass_batted_passes&ccomp%5B15%5D=gt&cstat%5B15%5D=pocket_time&ccomp%5B16%5D=gt&cstat%5B16%5D=pass_rpo"