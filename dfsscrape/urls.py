
"""
NCAA TOURNEY
"""
# all since 1985
NCAAM_MM_FIRST4_85_TO_24 = "https://stathead.com/basketball/cbb/team-game-finder.cgi?request=1&timeframe=seasons&year_min=1985&comp_type=ncaat&tourn_id=f4&comp_id=NCAAM"
NCAAM_MM_64_85_TO_24 = "https://stathead.com/basketball/cbb/team-game-finder.cgi?request=1&timeframe=seasons&year_min=1985&comp_type=ncaat&tourn_id=r64&comp_id=NCAAM"
NCAAM_MM_32_85_TO_24 = "https://stathead.com/basketball/cbb/team-game-finder.cgi?request=1&timeframe=seasons&year_min=1985&comp_type=ncaat&tourn_id=r32&comp_id=NCAAM"
NCAAM_MM_REGIONAL_85_TO_24 = "https://stathead.com/basketball/cbb/team-game-finder.cgi?request=1&timeframe=seasons&year_min=1985&comp_type=ncaat&tourn_id=reg&comp_id=NCAAM"
NCAAM_MM_FINAL4_85_TO_24 = "https://stathead.com/basketball/cbb/team-game-finder.cgi?request=1&timeframe=seasons&year_min=1985&comp_type=ncaat&tourn_id=ff&comp_id=NCAAM"

"""
NCAA REG SEASON
"""
def NCAAM_REG_SEASON_TEAM_PTS(year: str):
    return f"https://stathead.com/basketball/cbb/team-game-finder.cgi?request=1&timeframe=seasons&year_min={year}&year_max={year}&comp_type=reg&comp_id=NCAAM"

def NCAAM_REG_SEASON_TEAM_STATS(year: str):
    return f"https://stathead.com/basketball/cbb/team-game-finder.cgi?request=1&order_by_asc=1&order_by=team_name_abbr&timeframe=seasons&year_min={year}&year_max={year}&comp_type=reg&comp_id=NCAAM&ccomp%5B1%5D=gt&cstat%5B1%5D=orb&ccomp%5B2%5D=gt&cstat%5B2%5D=ast"

def NCAAM_REG_SEASON_TEAM_ADVANCED(year: str):
    return f"https://stathead.com/basketball/cbb/team-game-finder.cgi?request=1&order_by_asc=1&order_by=team_name_abbr&timeframe=seasons&year_min={year}&year_max={year}&comp_type=reg&comp_id=NCAAM&ccomp%5B4%5D=gt&cstat%5B4%5D=team_orb_pct&ccomp%5B5%5D=gt&cstat%5B5%5D=team_ast_pct&ccomp%5B6%5D=gt&cstat%5B6%5D=team_off_rtg"