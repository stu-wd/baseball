from fastapi import APIRouter
from cache import get_state
import config

router = APIRouter(prefix="/standings", tags=["standings"])


@router.get("")
def get_standings():
    state = get_state()
    return [
        {
            "seed": t.playoff_seed,
            "id": t.id,
            "name": t.name,
            "wins": t.wins,
            "losses": t.losses,
            "points_for": round(t.points_for, 1),
            "points_against": round(t.points_against, 1),
            "streak_type": t.streak_type,
            "streak_length": t.streak_length,
        }
        for t in state.get_standings()
    ]
