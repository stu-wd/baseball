from fastapi import APIRouter
from cache import get_state
from services import news as news_svc

router = APIRouter(prefix="/news", tags=["news"])


@router.get("")
def get_news():
    state = get_state()
    return news_svc.get_matchup_news(state)
