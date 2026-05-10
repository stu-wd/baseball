import { apiFetch } from "@/lib/api";
import type { WaiverProbable } from "@/lib/types";

export async function GET() {
  const data = await apiFetch<WaiverProbable[]>("/pitching/waiver-probables");
  return Response.json(data);
}
