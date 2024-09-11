select DISTINCT
player_name as name_display,
position as pos_game,
team as team_name_abbr,
proj.player_id,
week as week_num,
fpros_projection
from projections as proj
join players_dict as dict
on
proj.player_id = dict.player_id