"use client";

import { useQuery } from "@tanstack/react-query";
import { DataTable } from "@/components/data-table";
import type { PitchingStart } from "@/lib/types";

const COLUMNS = [
  { key: "Pitcher", label: "Pitcher" },
  { key: "Points", label: "Points", numeric: true },
  { key: "Time", label: "Time" },
  { key: "Date", label: "Date" },
  { key: "Game", label: "Game" },
];

async function fetchStarts(): Promise<Record<string, PitchingStart[]>> {
  const res = await fetch("/api/pitching/starts");
  if (!res.ok) throw new Error("Failed to fetch starts");
  return res.json();
}

export function ScheduledStarts({
  initialData,
}: {
  initialData: Record<string, PitchingStart[]>;
}) {
  const { data, isFetching, refetch } = useQuery({
    queryKey: ["pitching-starts"],
    queryFn: fetchStarts,
    initialData,
  });

  const teams = Object.entries(data);

  return (
    <div className="flex flex-col gap-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Scheduled Starts</h1>
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="text-sm px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 disabled:opacity-50"
        >
          {isFetching ? "Refreshing…" : "↻ Refresh"}
        </button>
      </div>

      {teams.length === 0 && (
        <p className="text-gray-400">No probable starts found for this matchup period.</p>
      )}

      {teams.map(([teamName, starts]) => (
        <div key={teamName} className="flex flex-col gap-3">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-semibold">{teamName}</h2>
            <span className="text-sm text-gray-400">{starts.length} starts</span>
          </div>
          <DataTable rows={starts as object[]} columns={COLUMNS} />
        </div>
      ))}
    </div>
  );
}
