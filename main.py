import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import standings, matchup, roster, pitching, players, news
from routers import cache as cache_router

app = FastAPI(title="Baseball API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(standings.router)
app.include_router(matchup.router)
app.include_router(roster.router)
app.include_router(pitching.router)
app.include_router(players.router)
app.include_router(news.router)
app.include_router(cache_router.router)


@app.get("/")
def root():
    return {"status": "ok"}
