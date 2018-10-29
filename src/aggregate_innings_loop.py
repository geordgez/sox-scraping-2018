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

for team_abbrev in team_abbrevs:
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
    runs_allowed_data = Counter()
    num_innings_counter = Counter()

    for fnidx, fn in enumerate(os.listdir(gamedata_folder_path)):
        gamedata_file_path = os.path.join(gamedata_folder_path, fn)
        # print(fn)
        if fnidx >= 0:
            df_games = pd.read_csv(gamedata_file_path)
            df_games.rename(index=str, columns={'Unnamed: 1': 'Team'}, inplace=True)

            # get rid of NaNs
            df_games = df_games[df_games['Team'] == df_games['Team']]

            # print(df_games['Team'].value_counts())
            df_by_teams = df_games.T.to_dict()

            for innings_idx in df_by_teams:
                innings_row = df_by_teams[innings_idx]
                # print(innings_row)

                # skip if row is game info row which doesn't have inning data
                if not innings_row['1'] == innings_row['1']:
                    continue

                innings_team = innings_row['Team']

                # print(innings_team)

                if not (innings_team == team_fullname):
                    # print(innings_row)
                    
                    runs_allowed = Counter({
                        k: int(str(v).replace('X', '0').replace('.0',''))
                        for k, v in innings_row.items() if k.isdigit()
                    })
                    runs_allowed_data += runs_allowed
                else:
                    innings_data_only = Counter({
                        k: int(str(v).replace('X', '0').replace('.0',''))
                        for k, v in innings_row.items() if k.isdigit()
                    })
                    all_innings_data += innings_data_only

            innings_indicators = Counter({
                k: 1 for k, v in innings_row.items() if v != 'X' and k.isdigit()
            })
            num_innings_counter += innings_indicators

    all_innings_data_list = list(list(e) for e in all_innings_data.items())
    runs_allowed_list = list(list(e) for e in runs_allowed_data.items())
    num_innings_list = list(list(e) for e in num_innings_counter.items())

    df_runs = pd.DataFrame(all_innings_data_list, columns=['inning_str', 'runs'])
    df_allowed = pd.DataFrame(runs_allowed_list, columns=['inning_str', 'allowed'])
    df_num_innings = pd.DataFrame(num_innings_list, columns=['inning_str', 'count'])

    df_runs = df_runs.merge(
        df_num_innings,
        how='right',
        left_on='inning_str',
        right_on='inning_str'
    ).merge(
        df_allowed,
        how='left',
        left_on='inning_str',
        right_on='inning_str'
    )

    df_runs.fillna(0, inplace=True)

    df_runs['average_scored'] = df_runs['runs'] /df_runs['count']
    df_runs['average_allowed'] = df_runs['allowed'] /df_runs['count']

    df_runs['inning_num'] = df_runs['inning_str'].map(int)
    df_runs = df_runs.sort_values('inning_num', axis=0)

    print(df_runs)

    run_data_output_path = os.path.join(team_folder_path, team_abbrev + '_runs_per_inning.csv')
    df_runs.to_csv(run_data_output_path, index=False)

    team_inning_data = df_games[df_games['Team'] == team_fullname]
    print(team_inning_data.shape)
