"""
Player game log history via pybaseball (Baseball Savant / Statcast).

Fetches pitch-level statcast data for a player-season and aggregates it
into per-game rows. Results are cached in SQLite (see db.py).

ESPN Fantasy player IDs are NOT MLBAM IDs. A name-based lookup via
pybaseball's playerid_lookup resolves the correct MLBAM ID, which is
then cached in SQLite so the lookup only happens once per player.
"""
from datetime import date

import pandas as pd

import db


def _season_date_range(season: int) -> tuple[str, str]:
    start = f"{season}-03-01"
    today = date.today()
    end = today.strftime("%Y-%m-%d") if today.year == season else f"{season}-11-01"
    return start, end


def _resolve_mlbam_id(espn_id: str, name: str) -> int | None:
    """Map an ESPN player ID to an MLBAM ID using the player's name.

    Result is cached in SQLite so the Chadwick Bureau lookup (slow on first
    call) only runs once per player.
    """
    cached = db.get_mlbam_id(espn_id)
    if cached is not None:
        return cached

    from pybaseball import playerid_lookup

    # Split "Elly De La Cruz" → first="Elly", last="De La Cruz"
    parts = name.strip().split(" ", 1)
    first = parts[0]
    last = parts[1] if len(parts) > 1 else ""

    try:
        result = playerid_lookup(last, first, fuzzy=False)
        if result.empty:
            result = playerid_lookup(last, first, fuzzy=True)
        if result.empty:
            return None
        mlbam_id = int(result.iloc[0]["key_mlbam"])
    except Exception:
        return None

    db.set_mlbam_id(espn_id, mlbam_id)
    return mlbam_id


def _aggregate_batter_logs(df: pd.DataFrame) -> list[dict]:
    """Aggregate pitch-level statcast data into per-game batter stats."""
    AB_EVENTS = {
        "single", "double", "triple", "home_run",
        "strikeout", "strikeout_double_play",
        "field_out", "grounded_into_double_play", "force_out",
        "fielders_choice", "fielders_choice_out",
        "double_play", "triple_play", "field_error",
        "sac_fly_double_play",
    }
    HIT_EVENTS = {"single", "double", "triple", "home_run"}

    logs = []
    group_cols = ["game_pk", "game_date", "home_team", "away_team", "batter"]
    for _, group in df.groupby(group_cols, sort=False):
        events = group["events"].dropna()
        ev = group["launch_speed"].dropna()
        la = group["launch_angle"].dropna()
        hard_hit = int((ev >= 95).sum()) if len(ev) else 0

        logs.append({
            "game_pk":          int(group["game_pk"].iloc[0]),
            "game_date":        str(group["game_date"].iloc[0]),
            "home_team":        str(group["home_team"].iloc[0]),
            "away_team":        str(group["away_team"].iloc[0]),
            "ab":               int(events.isin(AB_EVENTS).sum()),
            "h":                int(events.isin(HIT_EVENTS).sum()),
            "hr":               int((events == "home_run").sum()),
            "bb":               int(events.isin({"walk", "intent_walk"}).sum()),
            "k":                int(events.isin({"strikeout", "strikeout_double_play"}).sum()),
            "avg_exit_velo":    round(float(ev.mean()), 1) if len(ev) else None,
            "avg_launch_angle": round(float(la.mean()), 1) if len(la) else None,
            "hard_hit":         hard_hit,
        })

    logs.sort(key=lambda x: x["game_date"])
    return logs


def _aggregate_pitcher_logs(df: pd.DataFrame) -> list[dict]:
    """Aggregate pitch-level statcast data into per-game pitcher stats."""
    logs = []
    group_cols = ["game_pk", "game_date", "home_team", "away_team", "pitcher"]
    for _, group in df.groupby(group_cols, sort=False):
        events = group["events"].dropna()
        velocity = group["release_speed"].dropna()
        spin = group["release_spin_rate"].dropna()

        logs.append({
            "game_pk":       int(group["game_pk"].iloc[0]),
            "game_date":     str(group["game_date"].iloc[0]),
            "home_team":     str(group["home_team"].iloc[0]),
            "away_team":     str(group["away_team"].iloc[0]),
            "pitches":       int(len(group)),
            "k":             int(events.isin({"strikeout", "strikeout_double_play"}).sum()),
            "bb":            int(events.isin({"walk", "intent_walk"}).sum()),
            "hr_allowed":    int((events == "home_run").sum()),
            "avg_velocity":  round(float(velocity.mean()), 1) if len(velocity) else None,
            "avg_spin_rate": round(float(spin.mean()), 0) if len(spin) else None,
        })

    logs.sort(key=lambda x: x["game_date"])
    return logs


def get_game_logs(player_id: str, name: str, season: int, is_pitcher: bool) -> list[dict]:
    """
    Return per-game stats for a player-season.

    Resolves the ESPN player ID to an MLBAM ID via name lookup, then
    checks the SQLite cache. On a miss, fetches from Baseball Savant
    via pybaseball and caches the result.
    """
    cached = db.get_cached_game_logs(player_id, season)
    if cached is not None:
        return cached

    mlbam_id = _resolve_mlbam_id(player_id, name)
    if mlbam_id is None:
        return []

    if is_pitcher:
        from pybaseball import statcast_pitcher
        fetch_fn = statcast_pitcher
    else:
        from pybaseball import statcast_batter
        fetch_fn = statcast_batter

    start, end = _season_date_range(season)

    try:
        df = fetch_fn(start, end, player_id=mlbam_id)
    except Exception:
        return []

    if df is None or df.empty:
        return []

    logs = _aggregate_pitcher_logs(df) if is_pitcher else _aggregate_batter_logs(df)
    db.set_cached_game_logs(player_id, season, logs)
    return logs
