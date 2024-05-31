import update_tables
from interface import DFSDBInterface
import configure_db

default_config = configure_db.defaultConfig()
wrangler = update_tables.DataWrangler(DFSDBInterface(default_config))

wrangler.insert_contests_2023()
wrangler.insert_draftables()
wrangler.insert_payouts()
wrangler.match_player_names_2023()
wrangler.insert_ffanalytics_projections()
# wrangler.insert_player_results_2023()
