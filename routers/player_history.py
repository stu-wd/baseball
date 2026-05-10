from fastapi import APIRouter, HTTPException, Query

import config
from cache import get_state
from services import player_history as history_svc

router = APIRouter(prefix="/players", tags=["player-history"])

_PITCHER_POSITION_IDS = {1, 11}  # SP=1, RP=11 in ESPN's defaultPositionId


def _resolve_is_pitcher(player_id: str, type_param: str | None) -> bool:
    """Determine batter/pitcher from query param, falling back to LeagueState lookup."""
    if type_param == "pitcher":
        return True
    if type_param == "batter":
        return False

    # Auto-detect from current roster data
    state = get_state()
    for players in state.all_rosters.values():
        for p in players:
            if p.id == player_id:
                return (
                    p.default_position_id in _PITCHER_POSITION_IDS
                    or any(s in config.PITCHER_SLOT_IDS for s in p.eligible_slots)
                )

    raise HTTPException(
        status_code=400,
        detail=(
            f"Player {player_id} not found on any roster. "
            "Pass ?type=batter or ?type=pitcher explicitly."
        ),
    )


@router.get("/{player_id}/history")
def get_player_history(
    player_id: str,
    season: int = Query(default=config.SEASON_ID),
    type: str | None = Query(default=None, pattern="^(batter|pitcher)$"),
):
    is_pitcher = _resolve_is_pitcher(player_id, type)

    # Grab player name from roster for context (best-effort)
    name: str | None = None
    state = get_state()
    for players in state.all_rosters.values():
        for p in players:
            if p.id == player_id:
                name = p.name
                break
        if name:
            break

    if not name:
        raise HTTPException(status_code=400, detail="Player not found on any roster — cannot resolve MLBAM ID without a name.")

    logs = history_svc.get_game_logs(player_id, name, season, is_pitcher)

    return {
        "player_id": player_id,
        "name":      name,
        "type":      "pitcher" if is_pitcher else "batter",
        "season":    season,
        "game_logs": logs,
    }
