const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function POST() {
  const res = await fetch(`${API_URL}/cache/refresh`, { method: "POST" });
  if (!res.ok) {
    return Response.json({ error: "Failed to invalidate cache" }, { status: 502 });
  }
  return Response.json({ status: "invalidated" });
}
