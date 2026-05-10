import { apiFetch } from "@/lib/api";
import type { DailyScores } from "@/lib/types";

function ScoreColumn({ title, scores }: { title: string; scores: Record<string, number> }) {
  const sorted = Object.entries(scores).sort((a, b) => b[1] - a[1]);
  return (
    <div>
      <h2 className="text-lg font-semibold mb-3 text-gray-300">{title}</h2>
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="text-left text-gray-400 border-b border-gray-700">
            <th className="py-2 pr-4">Team</th>
            <th className="py-2 text-right">Points</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map(([team, pts]) => (
            <tr key={team} className="border-b border-gray-800 hover:bg-gray-800">
              <td className="py-2 pr-4">{team}</td>
              <td className="py-2 text-right font-mono">{pts.toFixed(1)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default async function ScoreboardPage() {
  const scores = await apiFetch<DailyScores>("/matchup/daily-scores");

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Daily Scoreboard</h1>
      <div className="grid grid-cols-2 gap-8">
        <ScoreColumn title="Today" scores={scores.Today} />
        <ScoreColumn title="Yesterday" scores={scores.Yesterday} />
      </div>
    </div>
  );
}
