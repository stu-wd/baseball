import { apiFetch } from "@/lib/api";
import { MatchupPlayerStats } from "@/components/matchup-player-stats";
import type { MatchupOverview, MatchupPlayerStats as MatchupPlayerStatsType } from "@/lib/types";

function ScoreCard({ name, score, delta }: { name: string; score: number; delta?: number }) {
  return (
    <div className="bg-gray-800 rounded-lg p-6 flex flex-col gap-1">
      <p className="text-sm text-gray-400">{name}</p>
      <p className="text-4xl font-bold font-mono">{score.toFixed(1)}</p>
      {delta != null && (
        <p className={`text-sm font-medium ${delta >= 0 ? "text-green-400" : "text-red-400"}`}>
          {delta >= 0 ? "+" : ""}{delta.toFixed(1)} vs opp
        </p>
      )}
    </div>
  );
}

export default async function MatchupPage() {
  const [overview, playerStats] = await Promise.all([
    apiFetch<MatchupOverview>("/matchup/overview"),
    apiFetch<MatchupPlayerStatsType>("/matchup/player-stats"),
  ]);

  const myIsHome = overview.home_name === playerStats.my_team[0]?.Player
    ? true
    : overview.my_team_id != null;

  const myScore = overview.home_score;
  const oppScore = overview.away_score;
  const myName = overview.home_name;
  const oppName = overview.away_name;

  const delta = myScore - oppScore;

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="text-2xl font-bold mb-4">Matchup Overview</h1>
        <div className="grid grid-cols-2 gap-4 max-w-lg">
          <ScoreCard name={myName} score={myScore} delta={delta} />
          <ScoreCard name={oppName} score={oppScore} />
        </div>
      </div>

      <MatchupPlayerStats
        myName={myName}
        oppName={oppName}
        initialData={playerStats}
      />
    </div>
  );
}
