#!/usr/bin/env python
import requests
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from tabulate import tabulate # I should check if this is installed
import os

import os

# Configuration
LEAGUE_ID = "1863581964"
MY_TEAM_ID = 9
SEASON_ID = 2026
ESPN_S2 = 'AECO3cUSj8Pt782PPobr4pB8ntD3YbuyE4TNhySfmcJdzaqIoKI2sKpeMVG5baKQqjhAIRQnUeOkJr54n2Oa6%2F8VeOplIQ3xFPEt%2FIfAjx4PXmDoLwaWpk8uiAXt78g4eL59GuVDEWAbtDruW4XManv2vkmAnJWBdj%2BF1Vxe3a%2Bw1OLjhLXW%2FcMlqHdrm4norQCXzs3C7heq2%2F1tKdXPVeDf%2F%2Bq3qbLigu9GiBR9XHtCU6hi58vR6DEY5FBjRKsisy%2BMd0ZadjBkrCbZztcdEN7r'
SWID = '{DEA1FB92-DABC-44DE-A1FB-92DABC74DE13}'
COOKIES = {'espn_s2': ESPN_S2, 'SWID': SWID}

def get_league_data(view):
    url = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb/seasons/{SEASON_ID}/segments/0/leagues/{LEAGUE_ID}?view={view}"
    response = requests.get(url, cookies=COOKIES)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch {view}: {response.status_code}")
        return None

def get_team_roster(team_id):
    url = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb/seasons/{SEASON_ID}/segments/0/leagues/{LEAGUE_ID}/teams/{team_id}?view=mRoster"
    response = requests.get(url, cookies=COOKIES)
    if response.status_code == 200:
        return response.json()
    return None

def get_mlb_scoreboard(date):
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={date}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def to_est_time(utc_string):
    dt_utc = datetime.strptime(utc_string, "%Y-%m-%dT%H:%MZ")
    dt_est = dt_utc.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/New_York"))
    return dt_est.strftime("%I:%M %p")

def get_current_matchup_opponent(team_id):
    data = get_league_data("mMatchupScore")
    if not data:
        return None, None
    
    scoring_period = data.get('scoringPeriodId')
    schedule = data.get('schedule', [])
    for m in schedule:
        if m.get('matchupPeriodId') == data['status']['currentMatchupPeriod']:
            home = m.get('home', {})
            away = m.get('away', {})
            if home.get('teamId') == team_id:
                return away.get('teamId'), data['status']['currentMatchupPeriod']
            if away.get('teamId') == team_id:
                return home.get('teamId'), data['status']['currentMatchupPeriod']
    return None, None

def get_team_pitchers(team_id):
    data = get_team_roster(team_id)
    if not data:
        return []
    
    pitchers = []
    # Position IDs: 1 (Pitcher), 11 (Probable Pitcher/RP/SP)
    for entry in data.get('roster', {}).get('entries', []):
        player = entry.get('playerPoolEntry', {}).get('player', {})
        pos_id = player.get('defaultPositionId')
        # Check primary position or games played
        pos_played = player.get('gamesPlayedByPosition', {})
        is_pitcher = pos_id in [1, 11] or any(p in ['1', '11'] for p in pos_played.keys())
        
        if is_pitcher:
            pitchers.append({
                'id': str(player.get('id')),
                'name': player.get('fullName'),
                'team_name': get_team_name(team_id)
            })
    return pitchers

team_names = {}

def load_team_names():
    global team_names
    data = get_league_data("mTeam")
    if data:
        for t in data.get('teams', []):
            team_names[t['id']] = t.get('name', f"Team {t['id']}")

def get_team_name(team_id):
    return team_names.get(team_id, f"Team {team_id}")

def get_all_mlb_probables(date_range):
    all_probables = []
    for date_str in date_range:
        scoreboard = get_mlb_scoreboard(date_str)
        if not scoreboard:
            continue
        
        for event in scoreboard.get('events', []):
            event_id = event['id']
            game_name = event['name']
            event_time = to_est_time(event['date'])
            for comp in event.get('competitions', []):
                for competitor in comp.get('competitors', []):
                    probables = competitor.get('probables', [])
                    for p in probables:
                        athlete = p.get('athlete', {})
                        all_probables.append({
                            'id': str(athlete.get('id')),
                            'name': athlete.get('fullName'),
                            'date': date_str,
                            'time': event_time,
                            'game': game_name
                        })
    return all_probables

def get_player_status_in_fantasy(player_ids):
    # Fetch mPlayerPool but limit to specific IDs to check ownership
    url = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb/seasons/{SEASON_ID}/segments/0/leagues/{LEAGUE_ID}?view=mPlayerPool"
    filters = {"players": {"filterIds": {"value": [int(i) for i in player_ids]}}}
    headers = {"x-fantasy-filter": json.dumps(filters)}
    
    response = requests.get(url, cookies=COOKIES, headers=headers)
    if response.status_code != 200:
        return {}
    
    data = response.json()
    ownership_map = {}
    for p in data.get('players', []):
        player_id = str(p.get('id'))
        team_id = p.get('onTeamId', 0)
        ownership_map[player_id] = team_id
    return ownership_map

def get_waiver_starts():
    load_team_names()
    today = datetime.now(ZoneInfo("America/New_York"))
    # Check next 7 days for waivers
    date_range = [(today + timedelta(days=i)).strftime("%Y%m%d") for i in range(8)]
    
    all_mlb_probables = get_all_mlb_probables(date_range)
    if not all_mlb_probables:
        return []
    
    unique_ids = list(set(p['id'] for p in all_mlb_probables))
    ownership_map = get_player_status_in_fantasy(unique_ids)
    
    waiver_starts = []
    for s in all_mlb_probables:
        on_team_id = ownership_map.get(s['id'], 0)
        if on_team_id == 0:
            s['Display Date'] = datetime.strptime(s['date'], "%Y%m%d").strftime("%a, %b %d")
            waiver_starts.append({
                'Pitcher': s['name'],
                'Time': s['time'],
                'Date': s['Display Date'],
                'Game': s['game']
            })
            
    return sorted(waiver_starts, key=lambda x: x['Date'])

def get_organized_starts():
    load_team_names()
    opponent_id, matchup_id = get_current_matchup_opponent(MY_TEAM_ID)
    if not opponent_id:
        return {}

    # Calculate dates
    today = datetime.now(ZoneInfo("America/New_York"))
    if matchup_id == 1:
        start_date = datetime(2026, 3, 25, tzinfo=ZoneInfo("America/New_York"))
        end_date = datetime(2026, 4, 5, tzinfo=ZoneInfo("America/New_York"))
    else:
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)

    # Convert date range to strings
    date_range = []
    curr = start_date
    while curr <= end_date:
        date_range.append(curr.strftime("%Y%m%d"))
        curr += timedelta(days=1)

    my_pitchers = get_team_pitchers(MY_TEAM_ID)
    opp_pitchers = get_team_pitchers(opponent_id)
    all_pitchers = my_pitchers + opp_pitchers
    pitcher_ids = set(p['id'] for p in all_pitchers)
    
    all_mlb_probables = get_all_mlb_probables(date_range)
    
    starts = []
    for s in all_mlb_probables:
        if s['id'] in pitcher_ids:
            p_info = next((p for p in all_pitchers if p['id'] == s['id']), {})
            s['team'] = p_info.get('team_name', 'Unknown')
            starts.append(s)
    
    if not starts:
        return {}

    # Group by Fantasy Team
    teams_dict = {}
    for s in starts:
        team_name = s['team']
        if team_name not in teams_dict:
            teams_dict[team_name] = []
        
        # Clean for display
        s['Display Date'] = datetime.strptime(s['date'], "%Y%m%d").strftime("%a, %b %d")
        teams_dict[team_name].append({
            'Pitcher': s['name'],
            'Time': s['time'],
            'Date': s['Display Date'],
            'Game': s['game']
        })
        
    return teams_dict

def main():
    load_team_names()
    print(f"Checking schedule for Team {get_team_name(MY_TEAM_ID)}...")
    opponent_id, matchup_id = get_current_matchup_opponent(MY_TEAM_ID)
    if not opponent_id:
        print("Couldn't find current matchup.")
        return

    print(f"Current Matchup: {get_team_name(MY_TEAM_ID)} vs {get_team_name(opponent_id)} (Matchup Period {matchup_id})")
    
    teams_dict = get_organized_starts()

    # Print each team's table
    for team_name, team_starts in teams_dict.items():
        print(f"\n{'-'*50}")
        print(f"STARTS FOR: {team_name.upper()}")
        print(f"Total Starts: {len(team_starts)}")
        print(f"{'-'*50}")
        
        table_data = []
        for s in team_starts:
            display_date = datetime.strptime(s['date'], "%Y%m%d").strftime("%a, %b %d")
            table_data.append([s['name'], s['time'], display_date, s['game']])
        
        headers = ["Pitcher", "Start Time", "Date", "Matchup"]
        try:
            print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
        except ImportError:
            print(f"{'Pitcher':<25} {'Time':<10} {'Date':<15} {'Matchup'}")
            for row in table_data:
                print(f"{row[0]:<25} {row[1]:<10} {row[2]:<15} {row[3]}")

if __name__ == "__main__":
    main()
