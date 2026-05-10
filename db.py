"""
SQLite cache for player game logs fetched from pybaseball/Baseball Savant.

Statcast calls are slow (5-10s per player-season). This cache stores the
aggregated results and refreshes every 6 hours during the active season.
"""
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "player_cache.db"
CACHE_TTL_HOURS = 6


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS player_game_logs (
                player_id   TEXT    NOT NULL,
                season      INTEGER NOT NULL,
                fetched_at  TEXT    NOT NULL,
                data        TEXT    NOT NULL,
                PRIMARY KEY (player_id, season)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mlbam_id_map (
                espn_id     TEXT PRIMARY KEY,
                mlbam_id    INTEGER NOT NULL
            )
        """)
        conn.commit()


def get_mlbam_id(espn_id: str) -> int | None:
    init_db()
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT mlbam_id FROM mlbam_id_map WHERE espn_id = ?", (espn_id,)
        ).fetchone()
    return int(row["mlbam_id"]) if row else None


def set_mlbam_id(espn_id: str, mlbam_id: int) -> None:
    init_db()
    with _get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO mlbam_id_map (espn_id, mlbam_id) VALUES (?, ?)",
            (espn_id, mlbam_id),
        )
        conn.commit()


def get_cached_game_logs(player_id: str, season: int) -> list[dict] | None:
    """Return cached game logs if they exist and are fresh, else None."""
    init_db()
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT fetched_at, data FROM player_game_logs WHERE player_id = ? AND season = ?",
            (player_id, season),
        ).fetchone()

    if row is None:
        return None

    fetched_at = datetime.fromisoformat(row["fetched_at"])
    age = datetime.now(timezone.utc) - fetched_at
    if age > timedelta(hours=CACHE_TTL_HOURS):
        return None

    return json.loads(row["data"])


def set_cached_game_logs(player_id: str, season: int, data: list[dict]) -> None:
    """Upsert game logs into cache."""
    init_db()
    now = datetime.now(timezone.utc).isoformat()
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO player_game_logs (player_id, season, fetched_at, data)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(player_id, season) DO UPDATE SET
                fetched_at = excluded.fetched_at,
                data       = excluded.data
            """,
            (player_id, season, now, json.dumps(data)),
        )
        conn.commit()
