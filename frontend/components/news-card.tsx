import type { NewsItem } from "@/lib/types";

function stripHtml(text: string | null): string | null {
  if (!text) return null;
  return text.replace(/<[^>]+>/g, "").trim();
}

export function NewsCard({ item }: { item: NewsItem }) {
  return (
    <div className="border border-gray-700 rounded-lg p-5 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-4">
        <h2 className="text-base font-semibold leading-snug">{item.Headline}</h2>
        <span className="text-xs text-gray-400 whitespace-nowrap shrink-0">{item.Date}</span>
      </div>

      {item.Players && (
        <p className="text-xs text-blue-400">{item.Players}</p>
      )}

      {item.Description && (
        <p className="text-sm text-gray-300">{stripHtml(item.Description)}</p>
      )}

      {item.Analysis && (
        <details className="group">
          <summary className="text-sm text-gray-400 cursor-pointer hover:text-gray-200 list-none flex items-center gap-1">
            <span className="group-open:rotate-90 transition-transform inline-block">▶</span>
            Analysis
          </summary>
          <p className="text-sm text-gray-300 mt-2">{stripHtml(item.Analysis)}</p>
        </details>
      )}

      <div className="flex items-center gap-3 text-xs text-gray-500">
        {item.Type && <span>{item.Type}</span>}
        {item.Link && item.Link !== "#" && (
          <a
            href={item.Link}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-500 hover:underline"
          >
            Full story →
          </a>
        )}
      </div>
    </div>
  );
}
