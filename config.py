import os
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

LEAGUE_ID = "1863581964"
MY_TEAM_ID = 9
SEASON_ID = 2026

ESPN_S2 = os.getenv("ESPN_S2", "")
SWID = os.getenv("SWID", "")
COOKIES = {'espn_s2': ESPN_S2, 'SWID': SWID}

BASE_ESPN_URL = (
    f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb"
    f"/seasons/{SEASON_ID}/segments/0/leagues/{LEAGUE_ID}"
)

SEASON_START = datetime(2026, 3, 25, tzinfo=ZoneInfo("America/New_York"))

# Pitcher slot IDs in ESPN's fantasy system
PITCHER_SLOT_IDS = [11, 14, 15]  # 11=P, 14=SP, 15=RP

SLOT_NAMES = {
    0: 'C', 1: '1B', 2: '2B', 3: '3B', 4: 'SS',
    5: 'OF', 6: 'OF', 7: 'OF', 11: 'P', 12: 'UTIL',
    14: 'SP', 15: 'RP', 16: 'BE', 17: 'IL',
}

DEFAULT_FA_PITCHER_LIMIT = 50
CACHE_TTL_SECONDS = 300  # 5 minutes
