import time
import os
import pathlib
from enum import Enum
from itertools import product

from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from dfsscrape import urls
from dfsutil.timer import Timer

TIMER = Timer()

# URL = urls.NCAA_MM_FIRST4_85_TO_24
# OUTFILE = "../data_output/ncaam_first4.csv"

def filename_from_func(func, year):
    func_name = func.__name__.split('.')[-1].lower()
    parent_dir = pathlib.Path(__file__).parent.resolve()
    filepath = parent_dir / f'data/{func_name}_{year}.csv'
    return filepath

class MultipleEmptyColumnNamesException(Exception):
    pass


class TableType(Enum):
    DRAFT = 0
    PLAYER_GAME = 1
    TEAM_GAME = 2
    NCAAM_TEAM_GAMES = 3


def read_stathead_table(soup):
    table = soup.find('tbody')
    rows = table.find_all('tr')
    data_dict = {}
    data_list = []
    for r in rows:
        if len(r.find_all('td')) > 0:
            cols_data = {c.attrs['data-stat']: c.get_text() for c in r.contents}
            data_list.append(cols_data)
            # for key, val in cols_data.items():
            #     if key in data_dict.keys():
            #         data_dict[key].append(val)
            #     else:
            #         data_dict[key] = []
            #         data_dict[key].append(val)

    data_df = pd.DataFrame(data_list)
    return data_df


def read_stathead_pages(url: str):
    chrome_options = Options()
    chromedata = os.path.join(pathlib.Path(__file__).parent.absolute(), 'chrome-data')
    chrome_options.add_argument('--user-data-dir=' + chromedata)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    
    page_table_list = []

    try:
        # log in to stathead
        TIMER.flag_start_time('Get URL')
        driver.get(url)
        TIMER.flag_end_time('Get URL')
        while True:
            # Find results table to confirm the search executed
            TIMER.flag_start_time('Get Table')
            num_trials = 20
            for trial in range(num_trials):
                try:
                    time.sleep(0.1)
                    driver.find_element('xpath', '//*[@id="results"]/tbody/tr[1]')
                    break
                except NoSuchElementException:
                    if trial == num_trials:
                        raise Exception('Failed to load table')
            TIMER.flag_end_time('Get Table')

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            TIMER.flag_start_time('Read Table')
            page_table = read_stathead_table(soup)
            TIMER.flag_end_time('Read Table')
            
            page_table_list.append(page_table)
            print(page_table.iloc[-1].values)
            try:
                TIMER.flag_start_time('Get Next Page')
                next_page = driver.find_elements('xpath', '//*[@id="stathead_results"]/div[5]/a')
                next_page_found = False
                for n in next_page:
                    if n.text == 'Next Page':
                        next_page_found = True
                        driver.get(n.get_attribute('href'))

                if not next_page_found:
                    break
            except NoSuchElementException:
                break
            TIMER.flag_end_time('Get Next Page')

        driver.quit()
        
        TIMER.flag_start_time('Build DataFrame')
        if len(page_table_list) > 0:
            data = pd.concat(page_table_list)
            TIMER.flag_end_time('Build DataFrame')
            return data
    except:
        pass

    return pd.DataFrame()


if __name__ == '__main__':

    years = [str(val) for val in range(2005, 2024)]
    url_funcs = [
        urls.NFL_PLAYER_GAMES_OFFENSE_ST,
        urls.NFL_PLAYER_GAMES_DEFENSE_PUNTING,
        urls.NFL_PLAYER_GAMES_TOUCHES,
        urls.NFL_PLAYER_GAMES_PASSING,
        urls.NFL_PLAYER_GAMES_SKILL_OFFENSE,
        urls.NFL_PLAYER_GAMES_ADVANCED_DEFENSE,
        urls.NFL_PLAYER_GAMES_SNAP_COUNTS
    ]
    for url_func, year in product(url_funcs, years):
        filepath = filename_from_func(url_func, year)
        print(filepath)
        if not os.path.exists(filepath):
            data = read_stathead_pages(url_func(year))
            TIMER.print_timers()
            # if len(data) > 0:
                # data.to_csv(filepath, header=True, index=False)
                