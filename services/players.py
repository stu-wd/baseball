"""
Player pool queries: free agents, waivers, ownership status.
These make their own ESPN API calls (FA data is not in LeagueState).
"""
from __future__ import annotations

import config
from api import espn

# Hitter slot IDs: C, 1B, 2B, 3B, SS, OF (×3), UTIL
_HITTER_SLOT_IDS = [0, 1, 2, 3, 4, 5, 6, 7, 12]


def get_top_free_agent_pitchers(limit: int = config.DEFAULT_FA_PITCHER_LIMIT) -> list[dict]:
    """Top unrostered pitchers sorted by ownership percentage."""
    filters = {
        "players": {
            "filterStatus": {"value": ["FREEAGENT", "WAIVERS"]},
            "filterSlotIds": {"value": [14, 15]},
            "sortPercOwned": {"sortPriority": 2, "sortAsc": False},
            "limit": limit,
        }
    }
    data = espn.fetch_player_pool(filters)

    players = []
    for p in data.get("players") or []:
        player = p.get("player") or {}
        eligible_slots = player.get("eligibleSlots") or []
        pos_labels = [
            config.SLOT_NAMES.get(s, str(s))
            for s in eligible_slots
            if s in config.PITCHER_SLOT_IDS
        ]
        players.append(
            {
                "Name": player.get("fullName"),
                "Owned %": round((player.get("ownership") or {}).get("percentOwned", 0), 1),
                "Status": p.get("status"),
                "Position": "/".join(pos_labels) if pos_labels else "P",
            }
        )
    return players


def get_free_agent_hitters(limit: int = 50) -> list[dict]:
    """Top unrostered hitters sorted by ownership percentage."""
    filters = {
        "players": {
            "filterStatus": {"value": ["FREEAGENT", "WAIVERS"]},
            "filterSlotIds": {"value": _HITTER_SLOT_IDS},
            "sortPercOwned": {"sortPriority": 2, "sortAsc": False},
            "limit": limit,
        }
    }
    data = espn.fetch_player_pool(filters)

    players = []
    for p in data.get("players") or []:
        player = p.get("player") or {}
        eligible_slots = player.get("eligibleSlots") or []
        pos_labels = [
            config.SLOT_NAMES.get(s, str(s))
            for s in eligible_slots
            if s in _HITTER_SLOT_IDS
        ]
        players.append(
            {
                "Name": player.get("fullName"),
                "Owned %": round((player.get("ownership") or {}).get("percentOwned", 0), 1),
                "Status": p.get("status"),
                "Position": "/".join(dict.fromkeys(pos_labels)) if pos_labels else "?",
            }
        )
    return players


def get_player_status(player_ids: list[str]) -> dict[str, dict]:
    """Ownership and fantasy team info for specific player IDs."""
    if not player_ids:
        return {}
    data = espn.fetch_player_status([int(i) for i in player_ids])
    result: dict[str, dict] = {}
    for p in data.get("players") or []:
        player_id = str(p.get("id"))
        player_obj = p.get("player") or {}
        result[player_id] = {
            "team_id": p.get("onTeamId", 0),
            "owned_pct": round((player_obj.get("ownership") or {}).get("percentOwned", 0), 1),
        }
    return result
