import { apiFetch } from "@/lib/api";
import { WaiverProbables } from "@/components/waiver-probables";
import type { WaiverProbable } from "@/lib/types";

export default async function WaiverProbablesPage() {
  const data = await apiFetch<WaiverProbable[]>("/pitching/waiver-probables");
  return <WaiverProbables initialData={data} />;
}
