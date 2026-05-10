"use client";

import { useRouter, useSearchParams } from "next/navigation";
import type { RosterTeam } from "@/lib/types";

export function TeamSelector({ teams, selectedId }: { teams: RosterTeam[]; selectedId: number }) {
  const router = useRouter();
  const searchParams = useSearchParams();

  function handleChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const params = new URLSearchParams(searchParams.toString());
    params.set("team", e.target.value);
    router.push(`/roster?${params.toString()}`);
  }

  return (
    <select
      value={selectedId}
      onChange={handleChange}
      className="bg-gray-700 text-sm px-3 py-2 rounded outline-none focus:ring-2 focus:ring-blue-500"
    >
      {teams.map((t) => (
        <option key={t.id} value={t.id}>
          {t.name}
        </option>
      ))}
    </select>
  );
}
