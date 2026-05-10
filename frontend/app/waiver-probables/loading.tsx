export default function Loading() {
  return (
    <div className="flex flex-col gap-4 animate-pulse">
      <div className="h-8 w-56 bg-gray-700 rounded" />
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <div key={i} className="h-8 bg-gray-800 rounded" />
      ))}
    </div>
  );
}
