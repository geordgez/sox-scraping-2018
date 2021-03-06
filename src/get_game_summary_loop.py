import os, errno
import json

import pandas as pd

import requests
import random
import time
from bs4 import BeautifulSoup as bs

# get list of all team URLs
teams_list_urls_path = '../data/all_teams_list.json'
with open(teams_list_urls_path, 'r') as infile:
    team_urls = json.load(infile)

team_abbrevs = [turl.split('.')[-1].split('/')[-1] for turl in team_urls]

# record number of pages scraped
pages_scraped = 0

for team_abbrev in team_abbrevs:

    input_folder = '../data/' + team_abbrev

    # make folder for storing results
    output_folder = '../data/' + team_abbrev + '/gamedata'
    try:
        os.makedirs(output_folder)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # get scraped URLs
    boxscore_urls_path = os.path.join(input_folder, 'boxscore_urls.json')
    with open(boxscore_urls_path, 'r') as infile:
        boxscore_urls = json.load(infile)

    # loop over all game URLs:
    for game_url in boxscore_urls:

        # get a good filename using the URL
        output_fn = ('/'.join(
            game_url.split('.')[-2].split('/')[-2:]).replace('/', '-')
            + '.csv'
        )
        output_fp = os.path.join(output_folder, output_fn)

        # don't scrape if the file already exists
        if os.path.exists(output_fp):
            continue

        print('#' + str(pages_scraped), 'output file path:', output_fp)

        # get game page soup
        page = requests.get(game_url)
        soup = bs(page.content, 'html.parser')

        # get boxscore table
        boxscore_wrapper = soup.find('div', {'class': 'linescore_wrap'})
        boxscore_table = boxscore_wrapper.find('table')
        df_box = pd.read_html(str(boxscore_table))[0]

        # write to csv
        df_box.to_csv(output_fp)

        pages_scraped += 1

        # wait a bit
        time_to_wait = min(10, 0.25 + random.expovariate(2))
        time.sleep(time_to_wait)
