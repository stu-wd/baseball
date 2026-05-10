"use client";

import { useQuery } from "@tanstack/react-query";
import { DataTable } from "@/components/data-table";
import type { WaiverProbable } from "@/lib/types";

const COLUMNS = [
  { key: "Pitcher", label: "Pitcher" },
  { key: "Owned %", label: "Owned %", numeric: true },
  { key: "Time", label: "Time" },
  { key: "Date", label: "Date" },
  { key: "Game", label: "Game" },
];

async function fetchWaiverProbables(): Promise<WaiverProbable[]> {
  const res = await fetch("/api/pitching/waiver-probables");
  if (!res.ok) throw new Error("Failed to fetch waiver probables");
  return res.json();
}

export function WaiverProbables({ initialData }: { initialData: WaiverProbable[] }) {
  const { data, isFetching, refetch } = useQuery({
    queryKey: ["waiver-probables"],
    queryFn: fetchWaiverProbables,
    initialData,
  });

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Waiver Wire Probables</h1>
          <p className="text-sm text-gray-400 mt-1">
            Unowned pitchers starting in the next 8 days
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="text-sm px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 disabled:opacity-50"
        >
          {isFetching ? "Refreshing…" : "↻ Refresh"}
        </button>
      </div>

      {data.length === 0 ? (
        <p className="text-gray-400">No unowned probable starters found for the next 8 days.</p>
      ) : (
        <>
          <p className="text-sm text-green-400">{data.length} available starts found</p>
          <DataTable rows={data as object[]} columns={COLUMNS} />
        </>
      )}
    </div>
  );
}
