import os
import json
from collections import Counter

import pandas as pd
import numpy as np

# get list of all teams
teams_list_urls_path = '../data/all_teams_list.json'
with open(teams_list_urls_path, 'r') as infile:
    team_urls = json.load(infile)

team_abbrevs = [turl.split('.')[-1].split('/')[-1] for turl in team_urls]

team_abbrev = team_abbrevs[0]
print(team_abbrev)

# make filepaths
team_folder_path = os.path.join('../data/', team_abbrev)
gamedata_folder_path = os.path.join(team_folder_path, 'gamedata/')

# find actual team name from abbreviation
teamnames_seen = []

for fn in os.listdir(gamedata_folder_path):
    gamedata_file_path = os.path.join(gamedata_folder_path, fn)
    # print(fn)
    df_game = pd.read_csv(gamedata_file_path)
    df_game.rename(index=str, columns={'Unnamed: 1': 'Team'}, inplace=True)
    game_teams = list(e for e in df_game['Team'].unique() if not e != e)
    teamnames_seen.extend(game_teams)

# most common team value is most likely team name
teamname_counter = Counter(teamnames_seen)
print('Probable team name:', teamname_counter.most_common(1))
