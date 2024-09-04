from typing import List
from itertools import product
import os
import requests
from lxml import html

from bs4 import BeautifulSoup
import pandas as pd
from dfsscrape import urls, config

# THESE ASSUME 2 ARGUMENTS: YEAR AND WEEK.  NEED TO REFACTOR IF ADDING SEASON-LONG PAGES
URL_FUNCS = [
    urls.NFL_COM_NFL_INJURY_REPORTS
]

def read_and_output_injury_report(url_func, year: str, week: int, replace=False):
    filepath = urls.filename_from_func(url_func, year, week=week)
    if replace or (not os.path.exists(filepath)):
        url = url_func(year, week)
        page = requests.get(url)
        # tree = html.fromstring(page.content)
        soup = BeautifulSoup(page.content, features='lxml')
        units = soup.find_all(class_='nfl-o-injury-report__unit')
        if len(units) == 0:
            raise config.NoDataException
        columns = [head.text.strip() for head in units[0].find(class_='d3-o-table--horizontal-scroll').find_all('th')]
        data = { head: [] for head in columns }
        data['Team'] = []
        for unit in units:
            teams = unit.find_all(class_='nfl-t-stats__title')
            teams = [tm.text.strip() for tm in teams]
            sections = unit.find_all(class_='d3-o-table--horizontal-scroll')
            for team, section in zip(teams, sections):
                headers = [th.text.strip() for th in section.find_all('th')]
                rows = section.find_all('tr')
                section_rows = []
                for row in rows[1:]: # first row is a header row
                    elements = row.find_all('td')
                    row_dict = {head: el.text.strip() for head, el in zip(headers, elements)}
                    section_rows.append(row_dict)
                data['Team'] += [team]*len(section_rows)
                for head in headers:
                    data[head] += [el[head] for el in section_rows]

        data = pd.DataFrame(data)
        if len(data) > 0:
            data.to_csv(filepath, header=True, index=False)
    else:
        print(f'File {filepath} already exists!')
            
def read_and_output_all(years: List[str], replace=False):
    for url_func, year in product(URL_FUNCS, years):
        for week in range(1, 19):
            try:
                read_and_output_injury_report(url_func, year, week, replace=replace)
            except config.NoDataException:
                print(f'No data found for year {year}, week {week}! Continuing...')
        
if __name__ == "__main__":
    years = [str(val) for val in range(2017, 2024)]
    read_and_output_all(years, replace=False)