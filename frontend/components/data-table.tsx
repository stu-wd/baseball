"use client";

import { useState } from "react";

interface DataTableProps {
  rows: object[];
  columns: { key: string; label: string; numeric?: boolean }[];
}

export function DataTable({ rows, columns }: DataTableProps) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortAsc, setSortAsc] = useState(false);

  function handleSort(key: string) {
    if (sortKey === key) {
      setSortAsc((a) => !a);
    } else {
      setSortKey(key);
      setSortAsc(false); // default descending for new column
    }
  }

  const sorted = sortKey
    ? [...rows].sort((a, b) => {
        const av = (a as Record<string, unknown>)[sortKey];
        const bv = (b as Record<string, unknown>)[sortKey];
        if (av == null) return 1;
        if (bv == null) return -1;
        const cmp =
          typeof av === "number" && typeof bv === "number"
            ? av - bv
            : String(av).localeCompare(String(bv));
        return sortAsc ? cmp : -cmp;
      })
    : rows;

  return (
    <table className="w-full text-sm border-collapse">
      <thead>
        <tr className="text-left text-gray-400 border-b border-gray-700">
          {columns.map((col) => (
            <th
              key={col.key}
              className={`py-2 pr-4 cursor-pointer select-none hover:text-gray-200 ${col.numeric ? "text-right" : ""}`}
              onClick={() => handleSort(col.key)}
            >
              {col.label}
              {sortKey === col.key ? (sortAsc ? " ↑" : " ↓") : ""}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {sorted.map((row, i) => (
          <tr key={i} className="border-b border-gray-800 hover:bg-gray-800">
            {columns.map((col) => {
              const val = (row as Record<string, unknown>)[col.key];
              return (
                <td
                  key={col.key}
                  className={`py-2 pr-4 ${col.numeric ? "text-right font-mono" : ""}`}
                >
                  {val != null ? String(val) : "—"}
                </td>
              );
            })}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
