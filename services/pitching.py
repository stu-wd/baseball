"""
Pitcher start logic: waiver wire probables and organized matchup starts.
Reads pitcher IDs from LeagueState (no per-team roster calls).
Still makes kona_player_info and MLB scoreboard calls — those are unavoidable.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import config
from api import espn, mlb
from services.league import LeagueState


def _to_est_time(utc_string: str) -> str:
    dt_utc = datetime.strptime(utc_string, "%Y-%m-%dT%H:%MZ")
    dt_est = dt_utc.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/New_York"))
    return dt_est.strftime("%I:%M %p")


def get_waiver_starts(state: LeagueState) -> list[dict]:
    """FA/waiver pitchers with a probable start in the next 8 days."""
    today = datetime.now(ZoneInfo("America/New_York"))
    date_range = [(today + timedelta(days=i)).strftime("%Y%m%d") for i in range(8)]

    # Fetch top 200 FA/waiver pitchers with their starter status
    filters = {
        "players": {
            "filterStatus": {"value": ["FREEAGENT", "WAIVERS"]},
            "filterSlotIds": {"value": [14, 15]},
            "sortPercOwned": {"sortPriority": 2, "sortAsc": False},
            "limit": 200,
        }
    }
    fa_data = espn.fetch_player_pool(filters)
    fa_players = fa_data.get("players") or []

    # Build map: proGameId -> list of (pitcher_name, owned_pct)
    starter_map: dict[str, list[tuple[str, float]]] = {}
    for p in fa_players:
        player = p.get("player") or {}
        name = player.get("fullName")
        owned_pct = round((player.get("ownership") or {}).get("percentOwned", 0), 1)
        starts = player.get("starterStatusByProGame") or {}
        for game_id, status in starts.items():
            if status == "PROBABLE":
                starter_map.setdefault(game_id, []).append((name, owned_pct))

    # Cross-reference with MLB scoreboard to get game details
    waiver_starts: list[dict] = []
    for date_str in date_range:
        try:
            scoreboard = mlb.fetch_scoreboard(date_str)
        except RuntimeError:
            continue

        display_date = datetime.strptime(date_str, "%Y%m%d").strftime("%a, %b %d")
        for event in scoreboard.get("events") or []:
            game_id = str(event["id"])
            if game_id not in starter_map:
                continue
            game_name = event["name"]
            event_time = _to_est_time(event["date"])
            for name, owned_pct in starter_map[game_id]:
                waiver_starts.append(
                    {
                        "Pitcher": name,
                        "Owned %": owned_pct,
                        "Time": event_time,
                        "Date": display_date,
                        "Game": game_name,
                    }
                )

    return sorted(
        waiver_starts,
        key=lambda x: datetime.strptime(x["Date"], "%a, %b %d").replace(year=config.SEASON_ID),
    )


def get_organized_starts(state: LeagueState) -> dict:
    """Probable starts for my team and my opponent during the current matchup week."""
    if state.current_matchup is None:
        return {}

    opp_id = state.current_matchup.opp_side.team_id
    matchup_id = state.current_matchup_period

    today = datetime.now(ZoneInfo("America/New_York"))

    if matchup_id == 1:
        start_date = config.SEASON_START
        end_date = datetime(config.SEASON_ID, 4, 5, tzinfo=ZoneInfo("America/New_York"))
    else:
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)

    # Build date range and scoring period map
    date_range: list[str] = []
    sp_map: dict[str, int] = {}
    curr = start_date
    while curr <= end_date:
        ds = curr.strftime("%Y%m%d")
        date_range.append(ds)
        sp_id = (curr - config.SEASON_START).days + 1
        if sp_id > 0:
            sp_map[ds] = sp_id
        curr += timedelta(days=1)

    # Fetch points for past/today scoring periods
    current_sp = (today - config.SEASON_START).days + 1
    relevant_sps = {sp for sp in sp_map.values() if sp <= current_sp}
    all_player_points: dict[tuple[str, int], float] = {}
    for sp in relevant_sps:
        try:
            data = espn.fetch_scoreboard(sp)
        except RuntimeError:
            continue
        for m in data.get("schedule") or []:
            if not m or not isinstance(m, dict):
                continue
            for side in ["home", "away"]:
                team_data = m.get(side) or {}
                roster = team_data.get("rosterForCurrentScoringPeriod") or {}
                for entry in roster.get("entries") or []:
                    if not entry or not isinstance(entry, dict):
                        continue
                    p_id = entry.get("playerId")
                    if p_id is None:
                        p_id = (entry.get("playerPoolEntry") or {}).get("playerId")
                    if p_id is not None:
                        pts = (entry.get("playerPoolEntry") or {}).get("appliedStatTotal", 0)
                        all_player_points[(str(p_id), sp)] = pts

    # Get pitcher IDs from state (no per-team API call)
    my_pitcher_ids = state.get_pitcher_ids(config.MY_TEAM_ID)
    opp_pitcher_ids = state.get_pitcher_ids(opp_id)
    all_pitcher_ids = my_pitcher_ids | opp_pitcher_ids

    # Build name map from state rosters
    name_map: dict[str, str] = {}
    for team_id in [config.MY_TEAM_ID, opp_id]:
        for player in state.all_rosters.get(team_id) or []:
            name_map[player.id] = player.name

    # Fetch MLB probable starters across the date range
    starts: list[dict] = []
    for date_str in date_range:
        try:
            scoreboard = mlb.fetch_scoreboard(date_str)
        except RuntimeError:
            continue
        for event in scoreboard.get("events") or []:
            event_time = _to_est_time(event["date"])
            game_name = event["name"]
            for comp in event.get("competitions") or []:
                for competitor in comp.get("competitors") or []:
                    for probable in competitor.get("probables") or []:
                        athlete = probable.get("athlete") or {}
                        p_id = str(athlete.get("id", ""))
                        if p_id not in all_pitcher_ids:
                            continue
                        sp = sp_map.get(date_str)
                        pts = all_player_points.get((p_id, sp)) if sp else None
                        display_date = datetime.strptime(date_str, "%Y%m%d").strftime("%a, %b %d")
                        starts.append(
                            {
                                "id": p_id,
                                "Pitcher": name_map.get(p_id, athlete.get("fullName", "Unknown")),
                                "team_name": state.get_team_name(
                                    config.MY_TEAM_ID if p_id in my_pitcher_ids else opp_id
                                ),
                                "Points": pts if pts is not None else "-",
                                "Time": event_time,
                                "Date": display_date,
                                "Game": game_name,
                            }
                        )

    if not starts:
        return {}

    # Group by fantasy team, my team first
    my_team_name = state.my_team_name
    teams_dict: dict[str, list[dict]] = {my_team_name: []}

    for s in starts:
        team_name = s["team_name"]
        teams_dict.setdefault(team_name, []).append(
            {k: v for k, v in s.items() if k not in ("id", "team_name")}
        )

    # Return my team first, then others, skip empties
    result: dict[str, list[dict]] = {}
    if teams_dict.get(my_team_name):
        result[my_team_name] = teams_dict[my_team_name]
    for name, team_starts in teams_dict.items():
        if name != my_team_name and team_starts:
            result[name] = team_starts

    return result
