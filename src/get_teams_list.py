import re
import json

import requests
from bs4 import BeautifulSoup as bs

# get teams list page soup
url = 'https://www.baseball-reference.com/leagues/MLB/2018.shtml'
page = requests.get(url)
soup = bs(page.content, 'html.parser')

# find all team season links
current_teams_container = soup.find('table', {'id': 'teams_standard_batting'})
team_url_suffixes = list(set([a['href'] for a in current_teams_container.find_all('a')]))

# make urls
three_caps_re = re.compile('/teams/[A-Z]{3}')
team_abbrevs = [
    three_caps_re.search(suffix).group()
    for suffix in team_url_suffixes
    if three_caps_re.search(suffix)
]
base_url = 'https://www.baseball-reference.com'
team_urls = [base_url + abbrev for abbrev in team_abbrevs]

# store to disk
all_teams_list_outpath = '../data/all_teams_list.json'
with open(all_teams_list_outpath, 'w') as outfile:
    json.dump(team_urls, outfile)
