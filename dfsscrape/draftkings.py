import os, shutil
from pathlib import Path
from datetime import timedelta, datetime
import json
import pandas as pd
import requests
from lxml import html
import time
import random
import webbrowser
import zipfile

from draft_kings import Client
from draft_kings.data import Sport

from dfsscrape.config import ScrapingConfig
from dfsutil.constants import DK_CONTEST_TYPES
from dfsscrape import utils
from dfsutil.dk_utils import get_nfl_week
from dfsdata.interface import DFSDBInterface


def get_contest_info(contest_id):
    url = f'https://api.draftkings.com/contests/v1/contests/{str(contest_id)}'
    page = requests.get(url)
    tree = html.fromstring(page.content)
    script = tree.xpath('/html/body/script[2]')
    # split off whitespace and comma at the end of the string
    script_json = script[0].text.split('let model = ')[1].split('txt = $$')[0].rstrip().rstrip(',')
    return json.loads(script_json)


def translate_contest_type(type_id):
    if str(type_id) in DK_CONTEST_TYPES:
        return DK_CONTEST_TYPES[str(type_id)]
    else:
        raise KeyError(f'DK contest type {str(type_id)} unknown.')


def file_is_fresh(filepath: Path) -> bool:
    """ True if file exists and was updated today

    :param filepath: path to file
    :return: True if file exists and was updated today
    """
    if not filepath.exists():
        return False
    mtime = os.path.getmtime(filepath)
    now_minus_1day = datetime.now() - timedelta(days=1)
    return datetime.fromtimestamp(mtime) > now_minus_1day

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def small_wait():
    time.sleep(random.uniform(0.5, 1.5))

def med_wait():
    time.sleep(random.uniform(5.0, 20.0))

def download_contest_entry_data():
    brave_path = 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'
    chrome_path = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
    browser = 'chrome'
    browser_path = chrome_path
    DATA_DUMP = ScrapingConfig().dk_data_path
    DOWNLOAD_DIR = 'C:\\Users\\Matthew\\Downloads\\'
    PREV_WEEK = get_nfl_week(str(ScrapingConfig().year)) - 1
    contest_id_list = DFSDBInterface().run_format_command('SELECT contest_id, entries_max FROM contests WHERE week=%s AND guaranteed = True AND entries_max >= 100', (str(PREV_WEEK),), fetch=True)
    
    # sort by entries max, descending, and get contest id only
    contest_id_list = [id[0] for id in sorted(contest_id_list.values, key=lambda x: x[1], reverse=True)]
    # contest_id_list = [id[0] for id in contest_id_list]

    # chromedriver = 'E:\\Chromedriver\\chromedriver-92'
    # chrome_options = webdriver.ChromeOptions()
    # prefs = {"download.default_directory": DOWNLOAD_DIR}
    # chrome_options.add_experimental_option("prefs", prefs)
    # chrome_options.add_argument("--user-data-dir=E:\\NFL_DFS\\scraping\\chrome-data")
    # os.environ["webdriver.chrome.driver"] = chromedriver
    # driver = webdriver.Chrome(chromedriver, options=chrome_options)
    # driver.implicitly_wait(10)
    # driver.get(windowpath)
    # time.sleep(10)

    webbrowser.register(browser, None, webbrowser.BackgroundBrowser(browser_path))
    webbrowser.get(browser).open_new('draftkings.com')
    med_wait()
    url = 'draftkings.com/contest/exportfullstandingscsv/' + str(contest_id_list[0])
    webbrowser.get(browser).open_new_tab(url)
    med_wait()
    dl_count = 0
    for dl_batch in chunks(contest_id_list, 30):
        dl_list = []
        dl_count += len(dl_batch)
        for cid in dl_batch:
            # get download file.  Download if not in data lake, or unzip and move if in download directory
            dl_file = os.path.join(DOWNLOAD_DIR, 'contest-standings-' + str(cid))
            if os.path.isfile(dl_file + '.zip'):
                try:
                    with zipfile.ZipFile(dl_file + '.zip', 'r') as zip_ref:
                        zip_ref.extractall(DATA_DUMP)
                except:
                    print('Failed to unzip:', dl_file)
                else:
                    os.remove(dl_file + '.zip')

            elif os.path.isfile(dl_file + '.csv'):
                shutil.move(dl_file + '.csv', DATA_DUMP)

            elif not os.path.isfile(os.path.join(DATA_DUMP, 'contest-standings-' + str(cid) + '.csv')):
                url = 'draftkings.com/contest/exportfullstandingscsv/' + str(cid)
                webbrowser.get(browser).open_new_tab(url)
                dl_list.append(dl_file)
                # small_wait()

            # else:
            #     print('Already have results for contest id:', cid)

        if len(dl_list) > 0:
            time.sleep(20)

        # unzip and/or move all files just downloaded
        for dl_file in dl_list:
            if os.path.isfile(dl_file + '.zip'):
                try:
                    with zipfile.ZipFile(dl_file + '.zip', 'r') as zip_ref:
                        zip_ref.extractall(DATA_DUMP)
                except:
                    print('Failed to unzip:', dl_file)
                else:
                    os.remove(dl_file + '.zip')

            elif os.path.isfile(dl_file + '.csv'):
                shutil.move(dl_file + '.csv', DATA_DUMP)

            else:
                print('Didn\'t find:', dl_file)

        print('Moving on to next batch')
        print('Downloaded/Found ' + str(dl_count) + ' out of ' + str(len(contest_id_list)) + ' contests meeting criteria')
        if len(dl_list) > 0:
            med_wait()


def main(download_list: bool = False):
    config = ScrapingConfig()
    contests_client = Client().contests(sport=Sport.NFL)
    contests = contests_client.contests
    groups = contests_client.draft_groups

    print('Number of Contests: ' + str(len(contests)))
    os.makedirs(config.dk_data_path, exist_ok=True)

    # make list of dictionaries for contests
    gametime_dict = {}
    contest_list = []
    for c in contests:
        contest_list_entry = {'id': c.contest_id, 'double_up': c.is_double_up, 'draft_group_id': c.draft_group_id,
                              'fantasy_player_points': c.fantasy_player_points, 'fifty_fifty': c.is_fifty_fifty,
                              'guaranteed': c.is_guaranteed, 'head_to_head': c.is_head_to_head, 'name': c.name,
                              'payout': c.payout, 'sport': c.sport.value, 'starred': c.is_starred}
        datestr = str(utils.utc_to_local(c.starts_at))
        contest_list_entry['starts_at'] = datestr
        details = c.entries_details
        contest_list_entry['entries_maximum'] = details.maximum
        contest_list_entry['entries_fee'] = details.fee
        contest_list_entry['entries_total'] = details.total
        contest_list_entry['draft_link'] = 'draftkings.com/draft/contest/' + str(contest_list_entry['id'])
        contest_list_entry['contest_link'] = 'draftkings.com/contest/gamecenter/' + str(contest_list_entry['id'])

        if datestr in gametime_dict:
            gametime_dict[datestr] += 1
        else:
            gametime_dict[datestr] = 1

        contest_list.append(contest_list_entry)

    # make list of dictionaries for draft groups
    draft_group_list = []
    for g in groups:
        draft_group_entry = {'draft_group_id': g.draft_group_id, 'series_id': g.series_id,
                             'contest_type_id': g.contest_type_id, 'sport_id': g.sport.value, 'sport': g.sport.value}
        datestr = str(utils.utc_to_local(g.starts_at))
        draft_group_entry['starts_at'] = datestr
        draft_group_entry['games_count'] = g.games_count

        draft_group_list.append(draft_group_entry)

    print(gametime_dict)

    # TODO: do I use this file? Investigate removing it and reading data as 'id' -> 'contest_id'
    outfile = config.dk_data_path / f'contest_list_{utils.get_today_string()}.json'
    with open(outfile, 'w') as f:
        json.dump(contest_list, f)

    # create table of contest details and draft group details
    contest_df = pd.DataFrame(contest_list).rename(columns={'id': 'contest_id'})
    contest_df = contest_df.drop_duplicates(subset=['contest_id'])
    draft_df = pd.DataFrame(draft_group_list)
    draft_df = draft_df.drop_duplicates(subset=['draft_group_id'])
    draft_group_table_file = config.dk_data_path / f'draft_group_table_{utils.get_today_string()}.csv'
    draft_df.to_csv(draft_group_table_file, index=False)

    contest_df = pd.merge(contest_df, draft_df[['draft_group_id', 'contest_type_id', 'games_count']], how='left', left_on='draft_group_id', right_on='draft_group_id')
    contest_df['contest_type'] = [translate_contest_type(type_id) for type_id in contest_df['contest_type_id']]
    contest_table_file = config.dk_data_path / f'contest_table_{utils.get_today_string()}.csv'
    contest_df.to_csv(contest_table_file, index=False)

    # Download draft group info files
    # filter out madden streams
    print('Getting Draft Group Files')
    contest_filter = contest_df.loc[contest_df['contest_type'] != 'Madden Stream']
    draft_groups = contest_filter['draft_group_id'].unique()
    for gid in draft_groups:
        filepath = config.dk_data_path / f'draft_group_info-{str(gid)}.json'
        if not file_is_fresh(filepath):
            utils.small_wait()
            draft = Client().draftables(draft_group_id=gid)
            draft_json = {
                'draftables': [],
                'competitions': []
            }
            for player in draft.players:
                player_json = {
                    'id': player.draftable_id,
                    'player_id': player.player_id,
                    'position': player.position_name,
                    'roster_slot_id': player.roster_slot_id,
                    'salary': player.salary,
                    'swappable': player.is_swappable,
                    'disabled': player.is_disabled,
                    'news_status': player.news_status_description,
                    'team_id': player.team_details.team_id,
                    'team_abbreviation': player.team_details.abbreviation,
                    'draft_alerts': player.draft_alerts,
                    'names': {
                        'first': player.name_details.first,
                        'last': player.name_details.last,
                        'display': player.name_details.display,
                        'short': player.name_details.short
                    },
                    'images': {
                        '50': player.image_details.fifty_pixels_by_fifty_pixels_url,
                        '160': player.image_details.one_hundred_and_sixty_pixels_by_one_hundred_and_sixty_pixels_url
                    }
                }
                try:
                    player_json['competition'] = {
                        'id': player.competition_details.competition_id,
                        'name': player.competition_details.name,
                        'starts_at': str(utils.utc_to_local(player.competition_details.starts_at))
                    }
                except AttributeError:
                    player_json['competition'] = None
                draft_json['draftables'].append(player_json)
            for comp in draft.competitions:
                comp_json = {
                    'id': comp.competition_id,
                    'name': comp.name,
                    'starts_at': str(utils.utc_to_local(comp.starts_at)),
                    'sport': comp.sport.value,
                    'venue': comp.venue,
                    'starting_lineups_available': comp.are_starting_lineups_available,
                    'depth_charts_available': comp.are_depth_charts_available,
                    'state': comp.state_description,
                    'home_team': {
                        'id': comp.home_team.team_id,
                        'name': comp.home_team.name,
                        'abbreviation': comp.home_team.abbreviation,
                        'city': comp.home_team.city
                    },
                    'away_team': {
                        'id': comp.away_team.team_id,
                        'name': comp.away_team.name,
                        'abbreviation': comp.away_team.abbreviation,
                        'city': comp.away_team.city
                    }
                }
                try:
                    comp_json['weather'] = {
                        'type': comp.weather.type,
                        'dome': comp.weather.dome
                    }
                except AttributeError:
                    comp_json['weather'] = None
                draft_json['competitions'].append(comp_json)
            # purge PlayerDraftAlertDetails objects
            for idx, alert in enumerate(draft_json['draftables']):
                if len(alert['draft_alerts']) > 0:
                    draft_json['draftables'][idx]['draft_alerts'] = []
            with open(filepath, 'w') as outfile:
                json.dump(draft_json, outfile)

        else:
            print('Already have data.  Moving to next group.')

    # Download contest info files (payouts)

    if download_list:
        contest_filter = contest_df.loc[(contest_df['contest_type'] != 'Madden Stream') & contest_df['guaranteed']]
        contest_ids = contest_filter['contest_id'].values
        for cid in contest_ids:
            filename = config.dk_data_path / f'contest_details-{str(cid)}.json'
            if not os.path.isfile(filename):
                utils.small_wait()
                print('Getting contest #' + str(cid))
                try:
                    info = get_contest_info(cid)
                    with open(filename, 'w') as outfile:
                        json.dump(info, outfile)
                except Exception as err:
                    print('Failed to connect!')


if __name__ == "__main__":
    # main(download_list=True)
    download_contest_entry_data()