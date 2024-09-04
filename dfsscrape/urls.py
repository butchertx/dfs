import pathlib
from dfsscrape.config import NFL_SEASON_DATA


def filename_from_func(func, year: str, week = None):
    func_name = func.__name__.split('.')[-1].lower()
    parent_dir = NFL_SEASON_DATA
    if week is not None:
        return parent_dir / f'{func_name}_{year}_week{str(week)}.csv'
    else:
        return parent_dir / f'{func_name}_{year}.csv'

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
def NFL_PLAYER_GAMES_OFFENSE_ST_(year: str):
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by=age_on_day&timeframe=seasons&year_min={year}&year_max={year}&comp_type=E&ccomp%5B1%5D=gt&cstat%5B1%5D=pass_cmp&ccomp%5B2%5D=gt&cstat%5B2%5D=rush_att&ccomp%5B3%5D=gt&cstat%5B3%5D=targets&ccomp%5B4%5D=gt&cstat%5B4%5D=all_td&ccomp%5B5%5D=gt&cstat%5B5%5D=fantasy_points&ccomp%5B6%5D=gt&cstat%5B6%5D=kick_ret&ccomp%5B7%5D=gt&cstat%5B7%5D=punt_ret"

def NFL_PLAYER_GAMES_DEFENSE_PUNTING_(year: str):
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by=age_on_day&timeframe=seasons&year_min={year}&year_max={year}&comp_type=E&ccomp%5B8%5D=gt&cstat%5B8%5D=sacks&ccomp%5B9%5D=gt&cstat%5B9%5D=def_int&ccomp%5B10%5D=gt&cstat%5B10%5D=fumbles&ccomp%5B11%5D=gt&cstat%5B11%5D=punt"

def NFL_PLAYER_GAMES_TOUCHES_(year: str):
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by=age_on_day&timeframe=seasons&year_min={year}&year_max={year}&comp_type=E&ccomp%5B10%5D=gt&cstat%5B10%5D=touches"

def NFL_PLAYER_GAMES_PASSING_(year: str):
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by=age_on_day&timeframe=seasons&year_min={year}&year_max={year}&comp_type=E&ccomp%5B2%5D=gt&cstat%5B2%5D=pass_target_yds&ccomp%5B3%5D=gt&cstat%5B3%5D=pass_batted_passes&ccomp%5B4%5D=gt&cstat%5B4%5D=pocket_time&ccomp%5B5%5D=gt&cstat%5B5%5D=pass_rpo"

def NFL_PLAYER_GAMES_SKILL_OFFENSE_(year: str):
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by=age_on_day&timeframe=seasons&year_min={year}&year_max={year}&comp_type=E&ccomp%5B5%5D=gt&cstat%5B5%5D=rec_air_yds&ccomp%5B6%5D=gt&cstat%5B6%5D=rush_yds_before_contact"

def NFL_PLAYER_GAMES_ADVANCED_DEFENSE_(year: str):
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by=age_on_day&timeframe=seasons&year_min={year}&year_max={year}&comp_type=E&ccomp%5B3%5D=gt&cstat%5B3%5D=def_targets"

def NFL_PLAYER_GAMES_SNAP_COUNTS_(year: str):
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by=age_on_day&timeframe=seasons&year_min={year}&year_max={year}&comp_type=E&ccomp%5B1%5D=gt&cstat%5B1%5D=snaps_offense"

"""
Refactored URLs with stats filters
"""
def NFL_PLAYER_GAMES_FANTASY(year: str):
    """
    """
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&timeframe=seasons&year_min={year}&year_max={year}"
    
def NFL_PLAYER_GAMES_PASSING(year: str):
    """
    Filters: >=1 pass attempt
    """
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by_asc=1&order_by=name_display_csk&timeframe=seasons&year_min={year}&year_max={year}&ccomp%5B2%5D=gt&cstat%5B2%5D=rush_att&ccomp%5B3%5D=gt&cstat%5B3%5D=all_td&ccomp%5B4%5D=gt&cstat%5B4%5D=fumbles&ccomp%5B5%5D=gt&cval%5B5%5D=1&cstat%5B5%5D=pass_att"

def NFL_PLAYER_GAMES_RUSHING(year: str):
    """
    Filters: >= 1 rush attempt
    """
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by_asc=1&order_by=name_display_csk&timeframe=seasons&year_min={year}&year_max={year}&ccomp%5B1%5D=gt&cval%5B1%5D=1&cstat%5B1%5D=rush_att&ccomp%5B2%5D=gt&cstat%5B2%5D=targets&ccomp%5B3%5D=gt&cstat%5B3%5D=all_td&ccomp%5B4%5D=gt&cstat%5B4%5D=kick_ret&ccomp%5B5%5D=gt&cstat%5B5%5D=punt_ret&ccomp%5B6%5D=gt&cstat%5B6%5D=fumbles&ccomp%5B7%5D=gt&cstat%5B7%5D=touches"

def NFL_PLAYER_GAMES_RECEIVING(year: str):
    """
    Filters: >= 1 target
    """
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by_asc=1&order_by=name_display_csk&timeframe=seasons&year_min={year}&year_max={year}&ccomp%5B2%5D=gt&cval%5B2%5D=1&cstat%5B2%5D=targets&ccomp%5B3%5D=gt&cstat%5B3%5D=all_td&ccomp%5B4%5D=gt&cstat%5B4%5D=kick_ret&ccomp%5B5%5D=gt&cstat%5B5%5D=punt_ret&ccomp%5B6%5D=gt&cstat%5B6%5D=fumbles&ccomp%5B7%5D=gt&cstat%5B7%5D=touches"

def NFL_PLAYER_GAMES_PASSING_ADV(year: str):
    """
    Filters: >= 1 pass attempt
    """
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by_asc=1&order_by=name_display_csk&timeframe=seasons&year_min={year}&year_max={year}&ccomp%5B1%5D=gt&cstat%5B1%5D=pass_target_yds&ccomp%5B2%5D=gt&cval%5B2%5D=1&cstat%5B2%5D=pass_att&ccomp%5B3%5D=gt&cstat%5B3%5D=pass_batted_passes&ccomp%5B4%5D=gt&cstat%5B4%5D=pocket_time&ccomp%5B5%5D=gt&cstat%5B5%5D=pass_rpo"

def NFL_PLAYER_GAMES_RECEIVING_RUSHING_ADV(year: str):
    """
    Filters: >= 1 touch
    """
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by_asc=1&order_by=name_display_csk&timeframe=seasons&year_min={year}&year_max={year}&ccomp%5B1%5D=gt&cstat%5B1%5D=rec_air_yds&ccomp%5B2%5D=gt&cstat%5B2%5D=rush_yds_before_contact&ccomp%5B3%5D=gt&cval%5B3%5D=1&cstat%5B3%5D=touches"

def NFL_PLAYER_GAMES_SNAP_COUNTS(year: str):
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by_asc=1&order_by=name_display_csk&timeframe=seasons&year_min={year}&year_max={year}&ccomp%5B4%5D=gt&cstat%5B4%5D=snaps_offense"

def NFL_PLAYER_GAMES_DEFENSE(year: str):
    """
    Filters: 0 pass att, 0 rush att, 0 targets
    """
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by_asc=1&order_by=name_display_csk&timeframe=seasons&year_min={year}&year_max={year}&ccomp%5B1%5D=gt&cstat%5B1%5D=sacks&ccomp%5B2%5D=gt&cstat%5B2%5D=def_int&ccomp%5B3%5D=gt&cstat%5B3%5D=fumbles&ccomp%5B4%5D=gt&cstat%5B4%5D=punt&ccomp%5B5%5D=eq&cval%5B5%5D=0&cstat%5B5%5D=pass_att&ccomp%5B7%5D=eq&cval%5B7%5D=0&cstat%5B7%5D=rush_att&ccomp%5B8%5D=eq&cval%5B8%5D=0&cstat%5B8%5D=targets"

def NFL_PLAYER_GAMES_DEFENSE_ADV(year: str):
    """
    Filters: 0 pass att, 0 rush att, 0 targets
    """
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by_asc=1&order_by=name_display_csk&timeframe=seasons&year_min={year}&year_max={year}&ccomp%5B5%5D=eq&cval%5B5%5D=0&cstat%5B5%5D=pass_att&ccomp%5B6%5D=eq&cval%5B6%5D=0&cstat%5B6%5D=rush_att&ccomp%5B7%5D=eq&cval%5B7%5D=0&cstat%5B7%5D=targets&ccomp%5B8%5D=gt&cstat%5B8%5D=def_targets"

def NFL_PLAYER_GAMES_KICKING_XP(year: str):
    """
    Filters: >=1 XPA
    """
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by_asc=1&order_by=name_display_csk&timeframe=seasons&year_min={year}&year_max={year}&ccomp%5B2%5D=gt&cstat%5B2%5D=punt&ccomp%5B3%5D=gt&cstat%5B3%5D=rush_att&ccomp%5B4%5D=gt&cstat%5B4%5D=pass_cmp&ccomp%5B5%5D=gt&cstat%5B5%5D=targets&ccomp%5B6%5D=gt&cstat%5B6%5D=draftkings_points&ccomp%5B7%5D=gt&cval%5B7%5D=1&cstat%5B7%5D=xpa"

def NFL_PLAYER_GAMES_KICKING_FG(year: str):
    """
    Filters: >=1 FGA
    """
    return f"https://stathead.com/football/player-game-finder.cgi?request=1&order_by_asc=1&order_by=name_display_csk&timeframe=seasons&year_min={year}&year_max={year}&ccomp%5B1%5D=gt&cstat%5B1%5D=punt&ccomp%5B2%5D=gt&cstat%5B2%5D=rush_att&ccomp%5B3%5D=gt&cstat%5B3%5D=pass_cmp&ccomp%5B4%5D=gt&cstat%5B4%5D=targets&ccomp%5B5%5D=gt&cstat%5B5%5D=draftkings_points&ccomp%5B7%5D=gt&cval%5B7%5D=1&cstat%5B7%5D=fga"

def NFL_PLAYER_GAMES_DUMMY(year: str):
    return f""

def NFL_TEAM_GAMES(year: str):
    return f"https://stathead.com/football/team-game-finder.cgi?request=1&order_by=team_name_abbr&timeframe=seasons&year_min={year}&year_max={year}&ccomp%5B1%5D=gt&cval%5B1%5D=0&cstat%5B1%5D=points&ccomp%5B2%5D=gt&cval%5B2%5D=0&cstat%5B2%5D=tot_yds&ccomp%5B3%5D=gt&cval%5B3%5D=0&cstat%5B3%5D=penalties&ccomp%5B4%5D=gt&cval%5B4%5D=0&cstat%5B4%5D=first_down&ccomp%5B5%5D=gt&cval%5B5%5D=0&cstat%5B5%5D=over_under"

##################################################################
# NFL.com URLs
##################################################################

def NFL_COM_NFL_INJURY_REPORTS(year: str, week: int, postseason=False):
    if postseason:
        return f"https://nfl.com/injuries/league/{year}/POST{str(week)}"
    else:
        return f"https://nfl.com/injuries/league/{year}/REG{str(week)}"