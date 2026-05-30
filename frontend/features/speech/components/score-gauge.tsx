"use client";

import { cn } from "@/lib/utils";

interface ScoreGaugeProps {
  label: string;
  value: number;
  suffix?: string;
  className?: string;
}

function scoreTone(value: number): string {
  if (value >= 80) return "text-emerald-400";
  if (value >= 60) return "text-sky-400";
  if (value >= 40) return "text-amber-400";
  return "text-red-400";
}

function barTone(value: number): string {
  if (value >= 80) return "bg-emerald-500";
  if (value >= 60) return "bg-sky-500";
  if (value >= 40) return "bg-amber-500";
  return "bg-red-500";
}

export function ScoreGauge({ label, value, suffix, className }: ScoreGaugeProps) {
  const clamped = Math.max(0, Math.min(100, value));

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-end justify-between gap-2">
        <span className="text-xs font-medium text-muted-foreground">{label}</span>
        <span className={cn("text-lg font-semibold tabular-nums", scoreTone(clamped))}>
          {Math.round(clamped)}
          {suffix ? (
            <span className="ml-0.5 text-xs font-normal text-muted-foreground">{suffix}</span>
          ) : null}
        </span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-muted/50">
        <div
          className={cn(
            "h-full rounded-full transition-all duration-700 ease-out",
            barTone(clamped),
          )}
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}
