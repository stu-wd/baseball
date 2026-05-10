import { apiFetch } from "@/lib/api";
import { NewsCard } from "@/components/news-card";
import type { NewsItem } from "@/lib/types";

export default async function NewsPage() {
  const items = await apiFetch<NewsItem[]>("/news");

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">News & Updates</h1>
      {items.length === 0 ? (
        <p className="text-gray-400">No recent news found for players in this matchup.</p>
      ) : (
        <div className="flex flex-col gap-4">
          {items.map((item, i) => (
            <NewsCard key={i} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}
