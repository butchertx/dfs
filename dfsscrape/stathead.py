import time
import os
import pathlib
from enum import Enum

from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from dfsscrape import urls

# URL = urls.NCAA_MM_FIRST4_85_TO_24
# OUTFILE = "../data_output/ncaam_first4.csv"


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

    # log in to stathead
    driver.get(url)
    page_table_list = []
    while True:
        try:
            time.sleep(2)
            # Find results table to confirm the search executed
            driver.find_element('xpath', '//*[@id="results"]/tbody/tr[1]')
        except NoSuchElementException:
            try:
                driver.find_element('xpath', '//*[@id="stats"]/tbody/tr[1]')
            except NoSuchElementException:
                break

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        page_table = read_stathead_table(soup)
        page_table_list.append(page_table)
        print(page_table.iloc[-1].values)
        try:
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

    driver.quit()
    if len(page_table_list) > 0:
        data = pd.concat(page_table_list)
        return data
    else:
        return 'No data'


if __name__ == '__main__':

    years = [str(val) for val in range(2005, 2025)]
    for year in years:
        data = read_stathead_pages(urls.NCAAM_REG_SEASON_TEAM_ADVANCED(year))
        data.to_csv(f'dfsscrape/data/reg_season_advanced_{year}.csv', header=True, index=False)