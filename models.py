from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Player:
    id: str
    name: str
    default_position_id: int
    eligible_slots: list[int]
    lineup_slot_id: int
    applied_stat_total: float       # matchup-period cumulative points
    today_points: float
    injury_status: str | None
    pro_team_id: int | None
    ownership_pct: float | None = None  # only populated for FA pool queries


@dataclass
class Team:
    id: int
    name: str
    abbrev: str
    wins: int
    losses: int
    points_for: float
    points_against: float
    playoff_seed: int
    streak_type: str
    streak_length: int


@dataclass
class MatchupSide:
    team_id: int
    total_points: float
    points_by_scoring_period: dict[str, float]  # sp_id (str) -> points
    roster: list[Player] = field(default_factory=list)        # rosterForMatchupPeriod (cumulative)
    today_roster: list[Player] = field(default_factory=list)  # rosterForCurrentScoringPeriod (today)


@dataclass
class Matchup:
    matchup_period_id: int
    home: MatchupSide
    away: MatchupSide
    my_side: MatchupSide    # reference to whichever side matches MY_TEAM_ID
    opp_side: MatchupSide
