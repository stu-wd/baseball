from fastapi import APIRouter
from cache import get_state
from services import pitching as pitching_svc

router = APIRouter(prefix="/pitching", tags=["pitching"])


@router.get("/starts")
def get_starts():
    state = get_state()
    return pitching_svc.get_organized_starts(state)


@router.get("/waiver-probables")
def get_waiver_probables():
    state = get_state()
    return pitching_svc.get_waiver_starts(state)
