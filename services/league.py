"""
LeagueState: loads all ESPN league data in two API calls and exposes it
as structured, in-memory objects. Every other service reads from a LeagueState
instance — they never re-fetch data that is already here.

Two ESPN calls on __init__:
  1. fetch_views(["mTeam", "mMatchupScore", "mMatchup"]) — teams, status, current matchup
  2. fetch_views(["mRoster"]) — all 12 teams' full rosters
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import config
from api import espn
from models import Matchup, MatchupSide, Player, Team


# ---------------------------------------------------------------------------
# Internal parsing helpers
# ---------------------------------------------------------------------------

def _parse_player(entry: dict) -> Player:
    pool = entry.get("playerPoolEntry") or {}
    player = pool.get("player") or {}
    return Player(
        id=str(entry.get("playerId") or player.get("id", "")),
        name=player.get("fullName", "Unknown"),
        default_position_id=player.get("defaultPositionId", 0),
        eligible_slots=player.get("eligibleSlots") or [],
        lineup_slot_id=entry.get("lineupSlotId", -1),
        applied_stat_total=pool.get("appliedStatTotal", 0.0),
        today_points=pool.get("appliedStatTotal", 0.0),  # overridden per roster type at call site
        injury_status=entry.get("injuryStatus"),
        pro_team_id=player.get("proTeamId"),
    )


def _parse_matchup_side(side_data: dict) -> MatchupSide:
    # Cumulative roster (rosterForMatchupPeriod) — used for period totals
    matchup_roster_raw = (side_data.get("rosterForMatchupPeriod") or {}).get("entries") or []
    matchup_roster = [_parse_player(e) for e in matchup_roster_raw if e]

    # Today's active roster (rosterForCurrentScoringPeriod) — used for today's points
    today_roster_raw = (side_data.get("rosterForCurrentScoringPeriod") or {}).get("entries") or []
    today_roster = [_parse_player(e) for e in today_roster_raw if e]

    return MatchupSide(
        team_id=side_data.get("teamId", 0),
        total_points=side_data.get("totalPoints", 0.0),
        points_by_scoring_period={
            str(k): float(v)
            for k, v in (side_data.get("pointsByScoringPeriod") or {}).items()
        },
        roster=matchup_roster,
        today_roster=today_roster,
    )


def _parse_team(t: dict) -> Team:
    overall = (t.get("record") or {}).get("overall") or {}
    overall_streak_type = overall.get("streakType", "")
    overall_streak_len = overall.get("streakLength", 0)
    return Team(
        id=t["id"],
        name=t.get("name", f"Team {t['id']}"),
        abbrev=t.get("abbrev", "???"),
        wins=overall.get("wins", 0),
        losses=overall.get("losses", 0),
        points_for=overall.get("pointsFor", 0.0),
        points_against=overall.get("pointsAgainst", 0.0),
        playoff_seed=t.get("playoffSeed", 99),
        streak_type=overall_streak_type,
        streak_length=overall_streak_len,
    )


# ---------------------------------------------------------------------------
# LeagueState
# ---------------------------------------------------------------------------

class LeagueState:
    """All league data loaded in two ESPN API calls.

    Instantiate once per Streamlit session; store in st.session_state.
    Check .is_stale() before reuse — if True, create a fresh instance.
    """

    def __init__(self) -> None:
        self.created_at = datetime.now(ZoneInfo("America/New_York"))

        # ── Call 1: teams + matchup status + current matchup rosters ──────
        combined = espn.fetch_views(["mTeam", "mMatchupScore", "mMatchup"])

        # Teams (from mTeam)
        self.teams: dict[int, Team] = {
            t["id"]: _parse_team(t)
            for t in (combined.get("teams") or [])
        }

        # League status (from mMatchupScore / mRoster — both carry status)
        status = combined.get("status") or {}
        self.current_matchup_period: int = int(status.get("currentMatchupPeriod", 0))
        self.scoring_period: int = int(status.get("latestScoringPeriod", 0))

        # Current matchup (from mMatchup schedule)
        self.current_matchup: Matchup | None = self._find_current_matchup(
            combined.get("schedule") or []
        )

        # ── Call 2: all teams' full rosters (mRoster) ─────────────────────
        roster_data = espn.fetch_views(["mRoster"])
        self.all_rosters: dict[int, list[Player]] = {}
        for team_entry in (roster_data.get("teams") or []):
            team_id = team_entry.get("id")
            if team_id is None:
                continue
            entries = (team_entry.get("roster") or {}).get("entries") or []
            self.all_rosters[team_id] = [_parse_player(e) for e in entries if e]

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _find_current_matchup(self, schedule: list[dict]) -> Matchup | None:
        for m in schedule:
            if not m or not isinstance(m, dict):
                continue
            if m.get("matchupPeriodId") != self.current_matchup_period:
                continue

            home_data = m.get("home") or {}
            away_data = m.get("away") or {}
            home_id = home_data.get("teamId")
            away_id = away_data.get("teamId")

            if home_id != config.MY_TEAM_ID and away_id != config.MY_TEAM_ID:
                continue

            home = _parse_matchup_side(home_data)
            away = _parse_matchup_side(away_data)
            my_side = home if home.team_id == config.MY_TEAM_ID else away
            opp_side = away if home.team_id == config.MY_TEAM_ID else home

            return Matchup(
                matchup_period_id=self.current_matchup_period,
                home=home,
                away=away,
                my_side=my_side,
                opp_side=opp_side,
            )
        return None

    # ── Public interface ─────────────────────────────────────────────────────

    def is_stale(self) -> bool:
        age = (datetime.now(ZoneInfo("America/New_York")) - self.created_at).total_seconds()
        return age > config.CACHE_TTL_SECONDS

    @property
    def my_team(self) -> Team | None:
        return self.teams.get(config.MY_TEAM_ID)

    @property
    def opponent(self) -> Team | None:
        if self.current_matchup is None:
            return None
        opp_id = self.current_matchup.opp_side.team_id
        return self.teams.get(opp_id)

    @property
    def my_team_name(self) -> str:
        t = self.my_team
        return t.name if t else f"Team {config.MY_TEAM_ID}"

    @property
    def opponent_name(self) -> str:
        t = self.opponent
        return t.name if t else "Opponent"

    def get_team_name(self, team_id: int) -> str:
        t = self.teams.get(team_id)
        return t.name if t else f"Team {team_id}"

    def get_standings(self) -> list[Team]:
        """All teams sorted by playoff seed (ascending = best first)."""
        return sorted(self.teams.values(), key=lambda t: t.playoff_seed)

    def get_pitcher_ids(self, team_id: int) -> set[str]:
        """IDs of all pitchers on a given fantasy team's roster."""
        players = self.all_rosters.get(team_id) or []
        return {
            p.id
            for p in players
            if p.default_position_id in [1, 11]  # pitcher default positions
            or any(s in config.PITCHER_SLOT_IDS for s in p.eligible_slots)
        }

    def get_daily_scores(self) -> dict:
        """Today and yesterday team totals — pure dict lookups, zero API calls."""
        if self.current_matchup is None:
            return {}

        my_name = self.my_team_name
        opp_name = self.opponent_name
        my_pbsp = self.current_matchup.my_side.points_by_scoring_period
        opp_pbsp = self.current_matchup.opp_side.points_by_scoring_period

        today_key = str(self.scoring_period)
        yesterday_key = str(self.scoring_period - 1)

        return {
            "Today": {
                my_name: my_pbsp.get(today_key, 0.0),
                opp_name: opp_pbsp.get(today_key, 0.0),
            },
            "Yesterday": {
                my_name: my_pbsp.get(yesterday_key, 0.0),
                opp_name: opp_pbsp.get(yesterday_key, 0.0),
            },
        }
