#!/usr/bin/env python
import requests
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from tabulate import tabulate # I should check if this is installed
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

def get_pitcher_starts(date, pitcher_ids):
    scoreboard = get_mlb_scoreboard(date)
    if not scoreboard:
        return []
    
    starts = []
    for event in scoreboard.get('events', []):
        for comp in event.get('competitions', []):
            for competitor in comp.get('competitors', []):
                probables = competitor.get('probables', [])
                for p in probables:
                    athlete = p.get('athlete', {})
                    a_id = str(athlete.get('id'))
                    if a_id in pitcher_ids:
                        starts.append({
                            'name': athlete.get('fullName'),
                            'date': date,
                            'time': to_est_time(event.get('date')),
                            'game': event.get('name')
                        })
    return starts

def main():
    load_team_names()
    print(f"Checking schedule for Team {get_team_name(MY_TEAM_ID)}...")
    opponent_id, matchup_id = get_current_matchup_opponent(MY_TEAM_ID)
    if not opponent_id:
        print("Couldn't find current matchup.")
        return

    print(f"Current Matchup: {MY_TEAM_ID} vs {opponent_id} (Matchup Period {matchup_id})")
    
    # Calculate dates for the matchup
    # If matchup_id == 1 and today is late March 2026
    # Let's just find "this week" (Monday to Sunday)
    # But user says first matchup is longer.
    # We can detect opening day. Opening day was likely March 25 or 26.
    
    today = datetime.now(ZoneInfo("America/New_York"))
    # Matchup Period 1 detection: March 25 onwards
    if matchup_id == 1:
        start_date = datetime(2026, 3, 25, tzinfo=ZoneInfo("America/New_York"))
        # End date for Matchup 1 is the following Sunday (not this one, but the next one usually?)
        # Actually in 2026, March 29 is Sunday. If March 25 is Wednesday.
        # Most leagues extend it to the NEXT Sunday April 5.
        end_date = datetime(2026, 4, 5, tzinfo=ZoneInfo("America/New_York"))
    else:
        # Standard weekly matchup (Monday to Sunday)
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)

    print(f"Matchup Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    my_pitchers = get_team_pitchers(MY_TEAM_ID)
    opp_pitchers = get_team_pitchers(opponent_id)
    
    all_pitchers = my_pitchers + opp_pitchers
    pitcher_map = {p['id']: p['name'] for p in all_pitchers}
    pitcher_ids = set(p['id'] for p in all_pitchers)
    
    starts = []
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y%m%d")
        print(f"Fetching probables for {date_str}...", end='\r')
        day_starts = get_pitcher_starts(date_str, pitcher_ids)
        for s in day_starts:
            # Tag with team info
            p_info = next((p for p in all_pitchers if p['name'] == s['name']), {})
            s['team'] = p_info.get('team_name', 'Unknown')
            starts.append(s)
        current_date += timedelta(days=1)
    
    print("\n" + "="*50)
    if not starts:
        print("No upcoming starts found for this matchup range.")
        return

    # Group by Fantasy Team
    teams_dict = {}
    for s in starts:
        team_name = s['team']
        if team_name not in teams_dict:
            teams_dict[team_name] = []
        teams_dict[team_name].append(s)

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
