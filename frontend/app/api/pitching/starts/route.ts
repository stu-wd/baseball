import { apiFetch } from "@/lib/api";
import type { PitchingStart } from "@/lib/types";

export async function GET() {
  const data = await apiFetch<Record<string, PitchingStart[]>>("/pitching/starts");
  return Response.json(data);
}
