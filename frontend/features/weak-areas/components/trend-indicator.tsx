"use client";

import { Minus, TrendingDown, TrendingUp } from "lucide-react";

import type { WeakAreaTrend } from "@/features/weak-areas/types";
import { cn } from "@/lib/utils";

interface TrendIndicatorProps {
  trend: WeakAreaTrend;
  delta?: number;
  className?: string;
}

export function TrendIndicator({ trend, delta, className }: TrendIndicatorProps) {
  if (trend === "insufficient_data") {
    return (
      <span className={cn("inline-flex items-center gap-1 text-xs text-muted-foreground", className)}>
        <Minus className="h-3.5 w-3.5" />
        Not enough data
      </span>
    );
  }

  const improving = trend === "improving";
  const Icon = improving ? TrendingUp : trend === "declining" ? TrendingDown : Minus;
  const label = improving ? "Improving" : trend === "declining" ? "Needs attention" : "Stable";
  const tone = improving
    ? "text-emerald-600 dark:text-emerald-400"
    : trend === "declining"
      ? "text-amber-600 dark:text-amber-400"
      : "text-muted-foreground";

  return (
    <span className={cn("inline-flex items-center gap-1 text-xs font-medium", tone, className)}>
      <Icon className="h-3.5 w-3.5" />
      {label}
      {delta != null && Math.abs(delta) >= 0.05 && (
        <span className="text-muted-foreground">({delta > 0 ? "+" : ""}{(delta * 100).toFixed(0)}%)</span>
      )}
    </span>
  );
}
