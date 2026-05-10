from fastapi import APIRouter, Query
from services import players as players_svc

router = APIRouter(prefix="/players", tags=["players"])


@router.get("/fa-pitchers")
def get_fa_pitchers(limit: int = Query(default=100, le=300)):
    return players_svc.get_top_free_agent_pitchers(limit=limit)


@router.get("/fa-hitters")
def get_fa_hitters(limit: int = Query(default=100, le=300)):
    return players_svc.get_free_agent_hitters(limit=limit)
