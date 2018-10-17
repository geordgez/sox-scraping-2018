import os, errno
import json

import pandas as pd

import requests
from bs4 import BeautifulSoup as bs

# get list of all team URLs
teams_list_urls_path = '../data/all_teams_list.json'
with open(teams_list_urls_path, 'r') as infile:
    team_urls = json.load(infile)

# get HTML page soup
for team_url in team_urls:

    # make folder for storing results
    team_abbrev = team_url.split('.')[-1].split('/')[-1]
    output_folder = os.path.join('../data/', team_abbrev)
    url = (
        'https://www.baseball-reference.com/teams/' +
        team_abbrev + '/2018-schedule-scores.shtml'
    )
    print(url)

    # get page
    page = requests.get(url)
    soup = bs(page.content, 'html.parser')

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
