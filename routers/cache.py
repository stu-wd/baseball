from fastapi import APIRouter
import cache

router = APIRouter(prefix="/cache", tags=["cache"])


@router.post("/refresh")
def refresh_cache():
    """Force a fresh LeagueState rebuild on the next request."""
    cache.invalidate()
    return {"status": "invalidated"}
