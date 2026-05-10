import { apiFetch } from "@/lib/api";
import type { PlayerHistory } from "@/lib/types";

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  const url = new URL(_req.url);
  const season = url.searchParams.get("season") ?? "";
  const type = url.searchParams.get("type") ?? "";

  const qs = new URLSearchParams();
  if (season) qs.set("season", season);
  if (type) qs.set("type", type);

  const data = await apiFetch<PlayerHistory>(
    `/players/${id}/history${qs.toString() ? `?${qs}` : ""}`,
  );
  return Response.json(data);
}
