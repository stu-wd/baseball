"""
News aggregation: fantasy player blurbs + general MLB articles.
Reads player IDs from LeagueState rosters — no redundant roster API calls.
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from api import mlb
from services.league import LeagueState


def _format_date(pub_date: str) -> str:
    try:
        dt = datetime.strptime(pub_date, "%Y-%m-%dT%H:%M:%SZ")
        dt_est = dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/New_York"))
        return dt_est.strftime("%b %d, %I:%M %p")
    except Exception:
        return pub_date


def get_matchup_news(state: LeagueState) -> list[dict]:
    """Latest fantasy blurbs and MLB articles for players in the current matchup."""
    if state.current_matchup is None:
        return []

    # Build player ID set and name map from state — no API calls
    player_ids: set[str] = set()
    player_map: dict[str, str] = {}
    for side in [state.current_matchup.my_side, state.current_matchup.opp_side]:
        for player in side.today_roster:
            player_ids.add(player.id)
            player_map[player.id] = player.name

    if not player_ids:
        return []

    relevant_news: list[dict] = []

    # Fantasy-specific player news (Rotowire-style blurbs)
    try:
        fantasy_data = mlb.fetch_fantasy_news(list(player_ids))
        for item in fantasy_data.get("feed") or []:
            p_id = str(item.get("playerId"))
            p_name = player_map.get(p_id, "Unknown Player")
            news_update = item.get("description") or item.get("headline")
            spin = item.get("story") if item.get("story") != item.get("description") else None
            relevant_news.append(
                {
                    "Headline": item.get("headline"),
                    "Description": news_update,
                    "Analysis": spin,
                    "Date": _format_date(item.get("published", "")),
                    "Type": item.get("type"),
                    "PlayerId": p_id,
                    "Players": p_name,
                    "Link": (item.get("links") or {}).get("web", {}).get("href", "#"),
                }
            )
    except RuntimeError:
        pass

    # General MLB news — filter to players in the matchup
    try:
        mlb_data = mlb.fetch_news(limit=50)
        for art in mlb_data.get("articles") or []:
            involved_players: list[str] = []
            is_relevant = False
            for cat in art.get("categories") or []:
                if cat.get("type") == "athlete":
                    p_id = str(cat.get("athleteId"))
                    involved_players.append(cat.get("description", ""))
                    if p_id in player_ids:
                        is_relevant = True
            if not is_relevant:
                continue
            # Deduplicate against fantasy feed
            if any(n["Headline"] == art.get("headline") for n in relevant_news):
                continue
            relevant_news.append(
                {
                    "Headline": art.get("headline"),
                    "Description": art.get("description"),
                    "Analysis": None,
                    "Date": _format_date(art.get("published", "")),
                    "Type": "Article",
                    "PlayerId": None,
                    "Players": ", ".join(involved_players),
                    "Link": (art.get("links") or {}).get("web", {}).get("href", "#"),
                }
            )
    except RuntimeError:
        pass

    return relevant_news
