from fastapi import APIRouter
from cache import get_state
from services import matchup as matchup_svc

router = APIRouter(prefix="/matchup", tags=["matchup"])


@router.get("/overview")
def get_overview():
    state = get_state()
    return matchup_svc.get_matchup_dashboard_data(state)


@router.get("/player-stats")
def get_player_stats():
    state = get_state()
    yesterday_pts = matchup_svc.get_yesterday_player_points(state)
    return matchup_svc.get_matchup_player_stats(state, yesterday_pts)


@router.get("/daily-scores")
def get_daily_scores():
    state = get_state()
    return state.get_daily_scores()
