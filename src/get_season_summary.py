import os, errno
import json

import pandas as pd

import requests
from bs4 import BeautifulSoup as bs

# get HTML page soup
url = 'https://www.baseball-reference.com/teams/BOS/2018-schedule-scores.shtml'
page = requests.get(url)
soup = bs(page.content, 'html.parser')

# make folder for storing results
team_abbrev = url.split('.')[-2].split('/')[-2]
output_folder = os.path.join('../data/', team_abbrev)

try:
    os.makedirs(output_folder)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

# find and convert table
table_wrapper = soup.find('div', {'id': 'all_team_schedule'})
table_html = str(table_wrapper.find('table'))
df_table = pd.read_html(table_html)[0]

table_output_path = os.path.join(output_folder, 'season_summary.csv')
df_table.to_csv(table_output_path)

# get links to each game summary
boxscore_elems = soup.find_all('td', {'data-stat': 'boxscore'})
boxscore_url_suffixes = [box_elem.find('a')['href'] for box_elem in boxscore_elems]

base_url = '/'.join(url.split('/')[:3])
boxscore_urls = ['/'.join([base_url, suffix]) for suffix in boxscore_url_suffixes]

boxscore_urls_path = os.path.join(output_folder, 'boxscore_urls.json')
with open(boxscore_urls_path, 'w') as outfile:
    json.dump(boxscore_urls, outfile)
