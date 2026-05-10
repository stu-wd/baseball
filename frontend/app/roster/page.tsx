import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { TeamSelector } from "@/components/team-selector";
import type { RosterTeam, RosterPlayer } from "@/lib/types";

export default async function RosterPage({
  searchParams,
}: {
  searchParams: Promise<{ team?: string }>;
}) {
  const { team } = await searchParams;
  const teams = await apiFetch<RosterTeam[]>("/roster");
  const selectedId = team ? parseInt(team) : teams[0]?.id;
  const roster = await apiFetch<RosterPlayer[]>(`/roster/${selectedId}`);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-4">
        <h1 className="text-2xl font-bold">Roster Browser</h1>
        <TeamSelector teams={teams} selectedId={selectedId} />
      </div>
      <p className="text-sm text-gray-400">{roster.length} players</p>
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="text-left text-gray-400 border-b border-gray-700">
            <th className="py-2 pr-4">Player</th>
            <th className="py-2 pr-4">Slot</th>
            <th className="py-2 pr-4 text-right">Total Pts</th>
            <th className="py-2">Status</th>
          </tr>
        </thead>
        <tbody>
          {roster.map((p) => (
            <tr key={p.id} className="border-b border-gray-800 hover:bg-gray-800">
              <td className="py-2 pr-4">
                <Link
                  href={`/players/${p.id}?type=${p.is_pitcher ? "pitcher" : "batter"}`}
                  className="text-blue-400 hover:text-blue-300 hover:underline"
                >
                  {p.name}
                </Link>
              </td>
              <td className="py-2 pr-4 text-gray-400">{p.slot}</td>
              <td className="py-2 pr-4 text-right font-mono">{p.total_points}</td>
              <td className="py-2 text-gray-400">{p.injury_status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
