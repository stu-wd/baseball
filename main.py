from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from logic import find_probables_per_team

# Import your actual functions here
# from your_module import find_probables_per_team

app = FastAPI()

# Optional: Allow frontend to access API (e.g., from React app at localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # use ["http://localhost:3000"] for stricter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/probables/{team_id}")
def get_probables(team_id: int):
    # Replace this with your real data fetch
    return find_probables_per_team(team_id)
