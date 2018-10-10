import json

import pandas as pd

import requests
from bs4 import BeautifulSoup as bs

# get HTML page soup
url = 'https://www.baseball-reference.com/teams/BOS/2018-schedule-scores.shtml'
page = requests.get(url)
soup = bs(page.content, 'html.parser')

# find and convert table
table_html = str(soup.find_all('table')[0])
df_table = pd.read_html(table_html)[0]

table_output_path = '../data/season_summary.csv'
df_table.to_csv(table_output_path)

# get links to each game summary
boxscore_elems = soup.find_all('td', {'data-stat': 'boxscore'})
boxscore_url_suffixes = [box_elem.find('a')['href'] for box_elem in boxscore_elems]

base_url = '/'.join(url.split('/')[:3])
boxscore_urls = ['/'.join([base_url, suffix]) for suffix in boxscore_url_suffixes]

boxscore_urls_path = '../data/boxscore_urls.json'
with open(boxscore_urls_path, 'w') as outfile:
    json.dump(boxscore_urls, outfile)
