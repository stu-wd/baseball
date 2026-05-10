import { apiFetch } from "@/lib/api";
import { DataTable } from "@/components/data-table";
import type { FreeAgent } from "@/lib/types";

const COLUMNS = [
  { key: "Name", label: "Name" },
  { key: "Owned %", label: "Owned %", numeric: true },
  { key: "Position", label: "Position" },
  { key: "Status", label: "Status" },
];

export default async function FAPitchersPage() {
  const players = await apiFetch<FreeAgent[]>("/players/fa-pitchers?limit=100");

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold">FA Pitchers</h1>
        <p className="text-sm text-gray-400 mt-1">
          Top 100 unrostered pitchers by ownership %
        </p>
      </div>
      <DataTable rows={players} columns={COLUMNS} />
    </div>
  );
}
