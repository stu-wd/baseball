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

def get_current_matchup_info():
    # mMatchupScore has the metadata like currentMatchupPeriod
    data = get_league_data("mMatchupScore")
    if not data:
        return None, None, None
    
    current_matchup_period = data['status']['currentMatchupPeriod']
    
    # mScoreboard is better for live scores and roster entry IDs
    sb_data = get_league_data("mScoreboard")
    if not sb_data:
        sb_data = data
        
    schedule = sb_data.get('schedule', [])
    
    matchup = None
    opponent_id = None
    for m in schedule:
        home = m.get('home', {})
        away = m.get('away', {})
        if home.get('teamId') == MY_TEAM_ID:
            matchup = m
            opponent_id = away.get('teamId')
            break
        if away.get('teamId') == MY_TEAM_ID:
            matchup = m
            opponent_id = home.get('teamId')
            break
                
    return opponent_id, current_matchup_period, matchup

def get_player_points_for_scoring_period(sp_id):
    # Fetch player points for a specific scoring period using mScoreboard
    data = get_league_data(f"mScoreboard&scoringPeriodId={sp_id}")
    if not data:
        return {}
    
    points_map = {}
    for m in data.get('schedule', []):
        for side in ['home', 'away']:
            team_data = m.get(side, {})
            roster = team_data.get('rosterForCurrentScoringPeriod', {})
            for entry in roster.get('entries', []):
                # Robust ID extraction
                p_id = entry.get('playerId')
                if p_id is None:
                    p_id = entry.get('playerPoolEntry', {}).get('playerId')
                if p_id is None:
                    p_id = entry.get('playerPoolEntry', {}).get('player', {}).get('id')
                
                if p_id:
                    points = entry.get('playerPoolEntry', {}).get('appliedStatTotal', 0)
                    points_map[str(p_id)] = points
    return points_map

def get_team_pitchers(team_id):
    data = get_team_roster(team_id)
    if not data:
        return []
    
    pitchers = []
    # Position IDs: 1 (Pitcher), 11 (Probable Pitcher/RP/SP)
    roster = data.get('roster') or {}
    for entry in roster.get('entries') or []:
        pool_entry = entry.get('playerPoolEntry') or {}
        player = pool_entry.get('player') or {}
        pos_id = player.get('defaultPositionId')
        # Check primary position or games played
        pos_played = player.get('gamesPlayedByPosition') or {}
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
        for t in data.get('teams') or []:
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
        player_obj = p.get('player') or {}
        ownership_map[player_id] = {
            'team_id': p.get('onTeamId', 0),
            'owned_pct': round((player_obj.get('ownership') or {}).get('percentOwned', 0), 1)
        }
    return ownership_map

def get_top_free_agent_pitchers(limit=50):
    url = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb/seasons/{SEASON_ID}/segments/0/leagues/{LEAGUE_ID}?view=kona_player_info"
    
    # filterSlotIds for Pitchers: 11 (P), 14 (SP), 15 (RP)
    # filterStatus: FREEAGENT, WAIVERS
    filters = {
        "players": {
            "filterStatus": {"value": ["FREEAGENT", "WAIVERS"]},
            "filterSlotIds": {"value": [14, 15]},
            "sortPercOwned": {"sortPriority": 2, "sortAsc": False},
            "limit": limit
        }
    }
    
    headers = {"x-fantasy-filter": json.dumps(filters)}
    response = requests.get(url, cookies=COOKIES, headers=headers)
    
    if response.status_code != 200:
        return []
        
    players = []
    # ESPN Slot IDs: 14=SP, 15=RP, 11=P (V3 labels vary, these are core)
    slot_names = {14: 'SP', 15: 'RP', 11: 'P', 5: 'OF', 4: 'SS', 3: '3B', 2: '2B', 1: '1B', 0: 'C', 12: 'UTIL'}
    
    for p in response.json().get('players', []):
        player = p.get('player') or {}
        eligible_slots = player.get('eligibleSlots') or []
        # Only show relevant pitching slots for the position string
        pos_labels = [slot_names.get(s, str(s)) for s in eligible_slots if s in [14, 15, 11]]
        
        players.append({
            'Name': player.get('fullName'),
            'Owned %': round((player.get('ownership') or {}).get('percentOwned', 0), 1),
            'Status': p.get('status'),
            'Position': '/'.join(pos_labels) if pos_labels else 'P',
        })
    return players

def get_waiver_starts():
    load_team_names()
    today = datetime.now(ZoneInfo("America/New_York"))
    date_range = [(today + timedelta(days=i)).strftime("%Y%m%d") for i in range(8)]
    
    # 1. Fetch free agent pitchers and their starter status
    # We fetch top 200 to cover almost all potential starters
    url = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb/seasons/{SEASON_ID}/segments/0/leagues/{LEAGUE_ID}?scoringPeriodId=3&view=kona_player_info"
    filters = {
        "players": {
            "filterStatus": {"value": ["FREEAGENT", "WAIVERS"]},
            "filterSlotIds": {"value": [14, 15]},
            "sortPercOwned": {"sortPriority": 2, "sortAsc": False},
            "limit": 200
        }
    }
    headers = {"x-fantasy-filter": json.dumps(filters)}
    response = requests.get(url, cookies=COOKIES, headers=headers)
    if response.status_code != 200:
        return []
        
    fa_players = response.json().get('players', [])
    starter_map = {} # proGameId -> list of (player_name, owned_pct)
    
    for p in fa_players:
        player = p.get('player', {})
        name = player.get('fullName')
        owned_pct = round((player.get('ownership') or {}).get('percentOwned', 0), 1)
        # Fix: handle case where starterStatusByProGame is null (None)
        starts = player.get('starterStatusByProGame') or {}
        for game_id, status in starts.items():
            if status == "PROBABLE":
                if game_id not in starter_map:
                    starter_map[game_id] = []
                starter_map[game_id].append((name, owned_pct))
    
    # 2. Map back to dates using MLB Scoreboard
    waiver_starts = []
    for date_str in date_range:
        scoreboard = get_mlb_scoreboard(date_str)
        if not scoreboard:
            continue
            
        display_date = datetime.strptime(date_str, "%Y%m%d").strftime("%a, %b %d")
        for event in scoreboard.get('events', []):
            game_id = str(event['id'])
            if game_id in starter_map:
                game_name = event['name']
                event_time = to_est_time(event['date'])
                for name, owned_pct in starter_map[game_id]:
                    waiver_starts.append({
                        'Pitcher': name,
                        'Owned %': owned_pct,
                        'Time': event_time,
                        'Date': display_date,
                        'Game': game_name
                    })
                        
    return sorted(waiver_starts, key=lambda x: datetime.strptime(x['Date'], "%a, %b %d").replace(year=2026))

def get_organized_starts():
    load_team_names()
    opponent_id, matchup_id, current_matchup = get_current_matchup_info()
    if not opponent_id:
        return {}

    # Calculate dates
    today = datetime.now(ZoneInfo("America/New_York"))
    # Season reference
    season_start = datetime(2026, 3, 25, tzinfo=ZoneInfo("America/New_York"))
    
    if matchup_id == 1:
        start_date = season_start
        end_date = datetime(2026, 4, 5, tzinfo=ZoneInfo("America/New_York"))
    else:
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)

    # Convert date range to strings and calculate Scoring Periods
    date_range = []
    sp_map = {} # date_str -> sp_id
    curr = start_date
    while curr <= end_date:
        ds = curr.strftime("%Y%m%d")
        date_range.append(ds)
        # SP calculation: days from March 25
        sp_id = (curr - season_start).days + 1
        if sp_id > 0:
            sp_map[ds] = sp_id
        curr += timedelta(days=1)

    # Get points for relevant SPs (past and today)
    # Today's SP
    current_sp = (today - season_start).days + 1
    all_player_points = {} # (player_id, sp_id) -> points
    
    # We only care about SPs that have happened or are happening
    relevant_sps = set(sp for ds, sp in sp_map.items() if sp <= current_sp)
    for sp in relevant_sps:
        sp_points = get_player_points_for_scoring_period(sp)
        for p_id, pts in sp_points.items():
            all_player_points[(p_id, sp)] = pts

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
            
            # Lookup points if the game is in the past or today
            ds = s['date']
            sp = sp_map.get(ds)
            pts = all_player_points.get((s['id'], sp))
            s['points'] = pts if pts is not None else "-"
            
            starts.append(s)
    
    if not starts:
        return {}

    # Group by Fantasy Team
    teams_dict = {}
    my_team_name = get_team_name(MY_TEAM_ID)
    
    # We want my_team_name to be first, then other teams.
    # Initializing with my_team_name (even if it might be empty later, we'll clean up)
    teams_dict[my_team_name] = []

    for s in starts:
        team_name = s['team']
        if team_name not in teams_dict:
            teams_dict[team_name] = []
        
        # Clean for display
        s['Display Date'] = datetime.strptime(s['date'], "%Y%m%d").strftime("%a, %b %d")
        teams_dict[team_name].append({
            'Pitcher': s['name'],
            'Points': s['points'],
            'Time': s['time'],
            'Date': s['Display Date'],
            'Game': s['game']
        })
        
    # Remove empty teams if they don't have starts, but keep my_team_name if it has starts
    final_dict = {}
    # First, add my team if it has starts
    if teams_dict.get(my_team_name):
        final_dict[my_team_name] = teams_dict[my_team_name]
    
    # Then add any other teams that have starts
    for t_name, t_starts in teams_dict.items():
        if t_name != my_team_name and t_starts:
            final_dict[t_name] = t_starts
            
    return final_dict

def get_matchup_dashboard_data():
    load_team_names()
    opp_id, matchup_id, matchup_data = get_current_matchup_info()
    if not matchup_data:
        return None
        
    home = matchup_data.get('home', {})
    away = matchup_data.get('away', {})
    
    return {
        'matchup_period': matchup_id,
        'home_name': get_team_name(home.get('teamId')),
        'home_score': home.get('totalPoints'),
        'away_name': get_team_name(away.get('teamId')),
        'away_score': away.get('totalPoints'),
        'my_team_id': MY_TEAM_ID
    }

def get_matchup_player_stats():
    load_team_names()
    opp_id, matchup_id, matchup_data = get_current_matchup_info()
    if not matchup_data:
        return None

    today = datetime.now(ZoneInfo("America/New_York"))
    season_start = datetime(2026, 3, 25, tzinfo=ZoneInfo("America/New_York"))
    current_sp = (today - season_start).days + 1
    yesterday_sp = current_sp - 1
    
    # We'll use get_team_roster (mRoster endpoint) for each team in the matchup to get the full current roster
    matchup_stats = {'my_team': [], 'opp_team': []}
    
    # Get points for yesterday
    yesterday_points = get_player_points_for_scoring_period(yesterday_sp) if yesterday_sp > 0 else {}
    
    # Also get matchup-long cumulative points for each player
    # We'll use mMatchup to get the cumulative totals for the current period
    m_data = get_league_data("mMatchup")
    m_info = [m for m in m_data.get('schedule', []) if m.get('id') == matchup_data['id']][0]
    cumulative_points = {}
    for side in ['home', 'away']:
        team_roster = m_info.get(side, {}).get('rosterForMatchupPeriod', {})
        for entry in team_roster.get('entries', []):
            p_id = str(entry.get('playerId'))
            cumulative_points[p_id] = entry.get('playerPoolEntry', {}).get('appliedStatTotal', 0)

    for side in ['my_team', 'opp_team']:
        t_id = MY_TEAM_ID if side == 'my_team' else opp_id
        roster_data = get_team_roster(t_id)
        if not roster_data:
            continue
            
        roster = roster_data.get('roster', {})
        for entry in roster.get('entries', []):
            player = entry.get('playerPoolEntry', {}).get('player', {})
            player_id = str(player.get('id'))
            name = player.get('fullName', 'Unknown Player')
            
            # Cumulative points
            total_pts = cumulative_points.get(player_id, 0)
            
            # Yesterday's points
            yest_pts = yesterday_points.get(player_id, 0)
            
            matchup_stats[side].append({
                'Player': name,
                'Yesterday': yest_pts,
                'Total': total_pts
            })
    
    # Sort by total points descending
    matchup_stats['my_team'].sort(key=lambda x: x['Total'], reverse=True)
    matchup_stats['opp_team'].sort(key=lambda x: x['Total'], reverse=True)
    
    return matchup_stats

def main():
    load_team_names()
    print(f"Checking schedule for Team {get_team_name(MY_TEAM_ID)}...")
    opponent_id, matchup_id, matchup_data = get_current_matchup_info()
    if not opponent_id:
        print("Couldn't find current matchup.")
        return

    print(f"Current Matchup: {get_team_name(MY_TEAM_ID)} vs {get_team_name(opponent_id)} (Matchup Period {matchup_id})")
    if matchup_data:
        home = matchup_data.get('home', {})
        away = matchup_data.get('away', {})
        print(f"Score: {get_team_name(home.get('teamId'))} {home.get('totalPoints')} - {get_team_name(away.get('teamId'))} {away.get('totalPoints')}")
    
    teams_dict = get_organized_starts()

    # Print each team's table
    for team_name, team_starts in teams_dict.items():
        print(f"\n{'-'*50}")
        print(f"STARTS FOR: {team_name.upper()}")
        print(f"Total Starts: {len(team_starts)}")
        print(f"{'-'*50}")
        
        table_data = []
        for s in team_starts:
            table_data.append([s['Pitcher'], s['Points'], s['Time'], s['Date'], s['Game']])
        
        headers = ["Pitcher", "Points", "Start Time", "Date", "Matchup"]
        try:
            print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
        except ImportError:
            print(f"{'Pitcher':<25} {'Time':<10} {'Date':<15} {'Matchup'}")
            for row in table_data:
                print(f"{row[0]:<25} {row[1]:<10} {row[2]:<15} {row[3]}")

if __name__ == "__main__":
    main()
