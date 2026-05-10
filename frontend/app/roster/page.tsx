import { apiFetch } from "@/lib/api";
import { DataTable } from "@/components/data-table";
import { TeamSelector } from "@/components/team-selector";
import type { RosterTeam, RosterPlayer } from "@/lib/types";

const COLUMNS = [
  { key: "name", label: "Player" },
  { key: "slot", label: "Slot" },
  { key: "total_points", label: "Total Pts", numeric: true },
  { key: "injury_status", label: "Status" },
];

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
      <DataTable rows={roster} columns={COLUMNS} />
    </div>
  );
}
