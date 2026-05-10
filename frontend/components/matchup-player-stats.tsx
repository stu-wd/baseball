"use client";

import { useQuery } from "@tanstack/react-query";
import { DataTable } from "@/components/data-table";
import type { MatchupPlayerStats } from "@/lib/types";

const COLUMNS = [
  { key: "Player", label: "Player" },
  { key: "Yesterday", label: "Yesterday", numeric: true },
  { key: "Total", label: "Total", numeric: true },
];

async function fetchPlayerStats(): Promise<MatchupPlayerStats> {
  const res = await fetch("/api/matchup/player-stats");
  if (!res.ok) throw new Error("Failed to fetch player stats");
  return res.json();
}

export function MatchupPlayerStats({
  myName,
  oppName,
  initialData,
}: {
  myName: string;
  oppName: string;
  initialData: MatchupPlayerStats;
}) {
  const { data, isFetching, refetch } = useQuery({
    queryKey: ["matchup-player-stats"],
    queryFn: fetchPlayerStats,
    initialData,
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Roster Comparison</h2>
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="text-sm px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 disabled:opacity-50"
        >
          {isFetching ? "Refreshing…" : "↻ Refresh"}
        </button>
      </div>
      <div className="grid grid-cols-2 gap-8">
        <div>
          <h3 className="text-sm font-medium text-gray-400 mb-2">{myName}</h3>
          <DataTable rows={data.my_team as object[]} columns={COLUMNS} />
        </div>
        <div>
          <h3 className="text-sm font-medium text-gray-400 mb-2">{oppName}</h3>
          <DataTable rows={data.opp_team as object[]} columns={COLUMNS} />
        </div>
      </div>
    </div>
  );
}
