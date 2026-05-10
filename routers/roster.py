from fastapi import APIRouter, HTTPException
from cache import get_state
import config

router = APIRouter(prefix="/roster", tags=["roster"])


@router.get("")
def list_teams():
    """All teams — used to populate the team selector."""
    state = get_state()
    return [{"id": t.id, "name": t.name} for t in state.get_standings()]


@router.get("/{team_id}")
def get_roster(team_id: int):
    state = get_state()
    players = state.all_rosters.get(team_id)
    if players is None:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
    return [
        {
            "id": p.id,
            "name": p.name,
            "slot": config.SLOT_NAMES.get(p.lineup_slot_id, str(p.lineup_slot_id)),
            "total_points": round(p.applied_stat_total, 1),
            "injury_status": p.injury_status or "ACTIVE",
            "is_pitcher": (
                p.default_position_id in (1, 11)
                or any(s in config.PITCHER_SLOT_IDS for s in p.eligible_slots)
            ),
        }
        for p in players
    ]
