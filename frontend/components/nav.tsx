"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { signOut } from "next-auth/react";
import { useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

const links = [
  { href: "/matchup", label: "Matchup Overview" },
  { href: "/scoreboard", label: "Daily Scoreboard" },
  { href: "/starts", label: "Scheduled Starts" },
  { href: "/waiver-probables", label: "Waiver Probables" },
  { href: "/fa-pitchers", label: "FA Pitchers" },
  { href: "/news", label: "News" },
  { href: "/standings", label: "Standings" },
  { href: "/roster", label: "Roster Browser" },
  { href: "/fa-hitters", label: "FA Hitters" },
];

export function Nav() {
  const pathname = usePathname();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [refreshing, setRefreshing] = useState(false);

  async function handleRefresh() {
    setRefreshing(true);
    try {
      await fetch("/api/cache/refresh", { method: "POST" });
      queryClient.invalidateQueries();
      router.refresh();
    } finally {
      setRefreshing(false);
    }
  }

  return (
    <nav className="flex flex-col h-full p-4 gap-1">
      <p className="text-lg font-bold mb-2">⚾ Baseball</p>
      <button
        onClick={handleRefresh}
        disabled={refreshing}
        className="mb-3 px-3 py-1.5 rounded text-xs bg-gray-700 hover:bg-gray-600 disabled:opacity-50 text-gray-300"
      >
        {refreshing ? "Refreshing…" : "↻ Refresh Data"}
      </button>
      {links.map(({ href, label }) => (
        <Link
          key={href}
          href={href}
          className={`px-3 py-2 rounded text-sm ${
            pathname === href
              ? "bg-blue-600 text-white"
              : "text-gray-300 hover:bg-gray-700"
          }`}
        >
          {label}
        </Link>
      ))}
      <button
        onClick={() => signOut({ callbackUrl: "/login" })}
        className="mt-auto px-3 py-2 rounded text-sm text-gray-400 hover:bg-gray-700 text-left"
      >
        Sign out
      </button>
    </nav>
  );
}
