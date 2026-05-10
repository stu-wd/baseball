export default function Loading() {
  return (
    <div className="flex flex-col gap-6 animate-pulse">
      <div className="flex flex-col gap-2">
        <div className="h-8 w-56 bg-gray-700 rounded" />
        <div className="h-4 w-40 bg-gray-800 rounded" />
      </div>
      <div className="flex flex-col gap-2">
        <div className="h-6 w-full bg-gray-800 rounded" />
        {Array.from({ length: 12 }).map((_, i) => (
          <div key={i} className="h-8 bg-gray-900 border border-gray-800 rounded" />
        ))}
      </div>
      <p className="text-sm text-gray-500">Fetching Statcast data — this may take a moment on first load…</p>
    </div>
  );
}
