"use client";

import type { RoadmapItemPriority } from "@/features/roadmap/types";

const CONFIG: Record<RoadmapItemPriority, { label: string; className: string }> = {
  high: { label: "High priority", className: "bg-red-500/15 text-red-400 border-red-500/30" },
  medium: { label: "Medium", className: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30" },
  low: { label: "Low", className: "bg-blue-500/15 text-blue-400 border-blue-500/30" },
};

export function RoadmapPriorityBadge({ priority }: { priority: RoadmapItemPriority }) {
  const { label, className } = CONFIG[priority];
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${className}`}
    >
      {label}
    </span>
  );
}
