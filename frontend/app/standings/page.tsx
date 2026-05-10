import { apiFetch } from "@/lib/api";
import type { TeamStanding } from "@/lib/types";

export default async function StandingsPage() {
  const teams = await apiFetch<TeamStanding[]>("/standings");

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">League Standings</h1>
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="text-left text-gray-400 border-b border-gray-700">
            <th className="py-2 pr-4">#</th>
            <th className="py-2 pr-4">Team</th>
            <th className="py-2 pr-4">W</th>
            <th className="py-2 pr-4">L</th>
            <th className="py-2 pr-4">PF</th>
            <th className="py-2 pr-4">PA</th>
            <th className="py-2">Streak</th>
          </tr>
        </thead>
        <tbody>
          {teams.map((t) => (
            <tr key={t.id} className="border-b border-gray-800 hover:bg-gray-800">
              <td className="py-2 pr-4 text-gray-400">{t.seed}</td>
              <td className="py-2 pr-4 font-medium">{t.name}</td>
              <td className="py-2 pr-4">{t.wins}</td>
              <td className="py-2 pr-4">{t.losses}</td>
              <td className="py-2 pr-4">{t.points_for}</td>
              <td className="py-2 pr-4">{t.points_against}</td>
              <td className="py-2">
                {t.streak_type ? `${t.streak_type[0]}${t.streak_length}` : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
