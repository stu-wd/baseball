import { apiFetch } from "@/lib/api";
import { ScheduledStarts } from "@/components/scheduled-starts";
import type { PitchingStart } from "@/lib/types";

export default async function StartsPage() {
  const data = await apiFetch<Record<string, PitchingStart[]>>("/pitching/starts");
  return <ScheduledStarts initialData={data} />;
}
