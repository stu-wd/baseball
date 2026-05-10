import { apiFetch } from "@/lib/api";
import type {
  PlayerHistory,
  BatterGameLog,
  PitcherGameLog,
} from "@/lib/types";

export default async function PlayerHistoryPage(
  props: PageProps<"/players/[id]">,
) {
  const { id } = await props.params;
  const { season, type } = await props.searchParams;

  const qs = new URLSearchParams();
  if (season && typeof season === "string") qs.set("season", season);
  if (type && typeof type === "string") qs.set("type", type);

  const data = await apiFetch<PlayerHistory>(
    `/players/${id}/history${qs.toString() ? `?${qs}` : ""}`,
  );

  const isBatter = data.type === "batter";

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold">
          {data.name ?? `Player ${id}`}
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          {data.season} · {isBatter ? "Batter" : "Pitcher"} ·{" "}
          {data.game_logs.length} games
        </p>
      </div>

      {data.game_logs.length === 0 ? (
        <p className="text-gray-500">No Statcast data found for this season.</p>
      ) : isBatter ? (
        <BatterTable logs={data.game_logs as BatterGameLog[]} />
      ) : (
        <PitcherTable logs={data.game_logs as PitcherGameLog[]} />
      )}
    </div>
  );
}

function BatterTable({ logs }: { logs: BatterGameLog[] }) {
  const reversed = [...logs].reverse();
  return (
    <table className="w-full text-sm border-collapse">
      <thead>
        <tr className="text-left text-gray-400 border-b border-gray-700">
          <th className="py-2 pr-4">Date</th>
          <th className="py-2 pr-4">Matchup</th>
          <th className="py-2 pr-3 text-right">AB</th>
          <th className="py-2 pr-3 text-right">H</th>
          <th className="py-2 pr-3 text-right">HR</th>
          <th className="py-2 pr-3 text-right">BB</th>
          <th className="py-2 pr-3 text-right">K</th>
          <th className="py-2 pr-3 text-right">EV</th>
          <th className="py-2 pr-3 text-right">LA</th>
          <th className="py-2 text-right">HH</th>
        </tr>
      </thead>
      <tbody>
        {reversed.map((g) => (
          <tr
            key={g.game_pk}
            className="border-b border-gray-800 hover:bg-gray-800"
          >
            <td className="py-2 pr-4 text-gray-300">{g.game_date}</td>
            <td className="py-2 pr-4 text-gray-400 text-xs">
              {g.away_team} @ {g.home_team}
            </td>
            <td className="py-2 pr-3 text-right font-mono">{g.ab}</td>
            <td className="py-2 pr-3 text-right font-mono">{g.h}</td>
            <td className="py-2 pr-3 text-right font-mono">{g.hr || "—"}</td>
            <td className="py-2 pr-3 text-right font-mono">{g.bb}</td>
            <td className="py-2 pr-3 text-right font-mono">{g.k}</td>
            <td className="py-2 pr-3 text-right font-mono">
              {g.avg_exit_velo ?? "—"}
            </td>
            <td className="py-2 pr-3 text-right font-mono">
              {g.avg_launch_angle ?? "—"}
            </td>
            <td className="py-2 text-right font-mono">{g.hard_hit}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function PitcherTable({ logs }: { logs: PitcherGameLog[] }) {
  const reversed = [...logs].reverse();
  return (
    <table className="w-full text-sm border-collapse">
      <thead>
        <tr className="text-left text-gray-400 border-b border-gray-700">
          <th className="py-2 pr-4">Date</th>
          <th className="py-2 pr-4">Matchup</th>
          <th className="py-2 pr-3 text-right">Pitches</th>
          <th className="py-2 pr-3 text-right">K</th>
          <th className="py-2 pr-3 text-right">BB</th>
          <th className="py-2 pr-3 text-right">HR</th>
          <th className="py-2 pr-3 text-right">Velo</th>
          <th className="py-2 text-right">Spin</th>
        </tr>
      </thead>
      <tbody>
        {reversed.map((g) => (
          <tr
            key={g.game_pk}
            className="border-b border-gray-800 hover:bg-gray-800"
          >
            <td className="py-2 pr-4 text-gray-300">{g.game_date}</td>
            <td className="py-2 pr-4 text-gray-400 text-xs">
              {g.away_team} @ {g.home_team}
            </td>
            <td className="py-2 pr-3 text-right font-mono">{g.pitches}</td>
            <td className="py-2 pr-3 text-right font-mono">{g.k}</td>
            <td className="py-2 pr-3 text-right font-mono">{g.bb}</td>
            <td className="py-2 pr-3 text-right font-mono">
              {g.hr_allowed || "—"}
            </td>
            <td className="py-2 pr-3 text-right font-mono">
              {g.avg_velocity ?? "—"}
            </td>
            <td className="py-2 text-right font-mono">
              {g.avg_spin_rate ?? "—"}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
