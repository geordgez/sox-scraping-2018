import os, errno
import json

import pandas as pd

import requests
import random
import time
from bs4 import BeautifulSoup as bs

input_folder = '../data/BOS'

# make folder for storing results
output_folder = '../data/BOS/gamedata'
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
    print('Output file path:', output_fp)

    # don't scrape if the file already exists
    if os.path.exists(output_fp):
        continue

    # get game page soup
    page = requests.get(game_url)
    soup = bs(page.content, 'html.parser')

    # get boxscore table
    boxscore_wrapper = soup.find('div', {'class': 'linescore_wrap'})
    boxscore_table = boxscore_wrapper.find('table')
    df_box = pd.read_html(str(boxscore_table))[0]

    # write to csv
    df_box.to_csv(output_fp)

    # wait a bit
    time_to_wait = min(10, 0.25 + random.expovariate(2))
    time.sleep(time_to_wait)
