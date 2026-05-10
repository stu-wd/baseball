"""
Matchup-specific computations.
All functions read from a LeagueState instance — zero ESPN API calls.
The one exception is get_yesterday_player_points() which fetches scoring period data.
"""
from __future__ import annotations

import config
from api import espn
from services.league import LeagueState


def get_matchup_dashboard_data(state: LeagueState) -> dict | None:
    """Summary scores for the current matchup header."""
    if state.current_matchup is None:
        return None

    home = state.current_matchup.home
    away = state.current_matchup.away

    return {
        "matchup_period": state.current_matchup_period,
        "home_name": state.get_team_name(home.team_id),
        "home_score": home.total_points,
        "away_name": state.get_team_name(away.team_id),
        "away_score": away.total_points,
        "my_team_id": config.MY_TEAM_ID,
    }


def get_yesterday_player_points(state: LeagueState) -> dict[str, float]:
    """Player-level points for yesterday's scoring period. Makes one ESPN API call."""
    yesterday_sp = state.scoring_period - 1
    if yesterday_sp <= 0:
        return {}

    data = espn.fetch_scoreboard(yesterday_sp)
    points_map: dict[str, float] = {}
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
                if p_id is None:
                    p_id = ((entry.get("playerPoolEntry") or {}).get("player") or {}).get("id")
                if p_id is not None:
                    points = (entry.get("playerPoolEntry") or {}).get("appliedStatTotal", 0)
                    points_map[str(p_id)] = points
    return points_map


def get_matchup_player_stats(
    state: LeagueState, yesterday_points: dict[str, float]
) -> dict | None:
    """Full roster comparison: cumulative period points + yesterday's points per player.

    Pass the result of get_yesterday_player_points(state) as yesterday_points
    so the caller controls when the API call happens (and can share the result).
    """
    if state.current_matchup is None:
        return None

    matchup_stats: dict[str, list[dict]] = {"my_team": [], "opp_team": []}

    for key, side in [
        ("my_team", state.current_matchup.my_side),
        ("opp_team", state.current_matchup.opp_side),
    ]:
        # Use the matchup-period roster for cumulative totals
        for player in side.roster:
            matchup_stats[key].append(
                {
                    "Player": player.name,
                    "Yesterday": yesterday_points.get(player.id, 0),
                    "Total": player.applied_stat_total,
                }
            )
        matchup_stats[key].sort(key=lambda x: x["Total"], reverse=True)

    return matchup_stats
