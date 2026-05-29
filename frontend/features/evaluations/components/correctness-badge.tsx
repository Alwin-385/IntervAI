"use client";

import { CheckCircle2, HelpCircle, XCircle } from "lucide-react";

import type { CorrectnessVerdict } from "@/features/evaluations/types";
import { cn } from "@/lib/utils";

const CONFIG: Record<
  CorrectnessVerdict,
  { label: string; className: string; Icon: typeof CheckCircle2 }
> = {
  correct: {
    label: "Correct",
    className: "border-emerald-500/40 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300",
    Icon: CheckCircle2,
  },
  partially_correct: {
    label: "Partially correct",
    className: "border-amber-500/40 bg-amber-500/10 text-amber-800 dark:text-amber-200",
    Icon: HelpCircle,
  },
  incorrect: {
    label: "Incorrect",
    className: "border-red-500/40 bg-red-500/10 text-red-700 dark:text-red-300",
    Icon: XCircle,
  },
};

interface CorrectnessBadgeProps {
  verdict: CorrectnessVerdict;
  className?: string;
}

export function CorrectnessBadge({ verdict, className }: CorrectnessBadgeProps) {
  const { label, className: tone, Icon } = CONFIG[verdict];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-sm font-medium",
        tone,
        className,
      )}
    >
      <Icon className="h-4 w-4 shrink-0" />
      {label}
    </span>
  );
}
