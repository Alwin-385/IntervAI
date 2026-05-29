"use client";

import type { WeakAreaPriority } from "@/features/weak-areas/types";
import { cn } from "@/lib/utils";

const styles: Record<WeakAreaPriority, string> = {
  high: "border-red-500/40 bg-red-500/10 text-red-700 dark:text-red-300",
  medium: "border-amber-500/40 bg-amber-500/10 text-amber-800 dark:text-amber-200",
  low: "border-emerald-500/40 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300",
};

interface PriorityBadgeProps {
  priority: WeakAreaPriority;
  className?: string;
}

export function PriorityBadge({ priority, className }: PriorityBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex rounded-full border px-2.5 py-0.5 text-xs font-semibold capitalize",
        styles[priority],
        className,
      )}
    >
      {priority}
    </span>
  );
}
