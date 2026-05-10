"""
Process-level LeagueState singleton.

get_state() is the single entry point — call it from every route handler.
It returns the cached instance if fresh, otherwise rebuilds it.
The threading.Lock prevents concurrent rebuilds when the cache is stale.
"""
import threading
from services.league import LeagueState

_state: LeagueState | None = None
_lock = threading.Lock()


def get_state() -> LeagueState:
    global _state
    with _lock:
        if _state is None or _state.is_stale():
            _state = LeagueState()
    return _state


def invalidate() -> None:
    """Force the next request to rebuild LeagueState (used by /cache/refresh)."""
    global _state
    with _lock:
        _state = None
