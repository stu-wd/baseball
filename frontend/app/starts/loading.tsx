export default function Loading() {
  return (
    <div className="flex flex-col gap-6 animate-pulse">
      <div className="h-8 w-48 bg-gray-700 rounded" />
      {[1, 2].map((i) => (
        <div key={i} className="flex flex-col gap-3">
          <div className="h-5 w-40 bg-gray-700 rounded" />
          {[1, 2, 3, 4].map((j) => (
            <div key={j} className="h-8 bg-gray-800 rounded" />
          ))}
        </div>
      ))}
    </div>
  );
}
