import os
import json
import re
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
team_fullname = teamname_counter.most_common(1)[0][0]
print('Probable team name:', team_fullname)

# aggregating inning data for the specific team
# TODO: clean up with above since looping through twice without caching data
# isn't efficient
all_innings_data = Counter()

for fnidx, fn in enumerate(os.listdir(gamedata_folder_path)):
    gamedata_file_path = os.path.join(gamedata_folder_path, fn)
    # print(fn)
    if fnidx >= 0:
        df_games = pd.read_csv(gamedata_file_path)
        df_games.rename(index=str, columns={'Unnamed: 1': 'Team'}, inplace=True)
        df_games = df_games[df_games['Team'] == team_fullname]
        df_by_teams = df_games.T.to_dict()

        for innings_idx in df_by_teams:
            innings_row = df_by_teams[innings_idx]
            innings_team = innings_row['Team']
            if not (innings_team == team_fullname):
                continue
            innings_data_only = Counter({
                k: int(str(v).replace('X', '0').replace('.0',''))
                for k, v in innings_row.items() if k.isdigit()
            })
            all_innings_data += innings_data_only

        # print(innings_team)
        # print(innings_data_only)

        # innings_team = df_by_team['Team']
        # print()
        # break

print(all_innings_data)

team_inning_data = df_games[df_games['Team'] == team_fullname]
print(team_inning_data.shape)
