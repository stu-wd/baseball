import { apiFetch } from "@/lib/api";
import type { MatchupPlayerStats } from "@/lib/types";

export async function GET() {
  const data = await apiFetch<MatchupPlayerStats>("/matchup/player-stats");
  return Response.json(data);
}
