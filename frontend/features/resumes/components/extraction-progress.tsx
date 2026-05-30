"use client";

import { CheckCircle2, Circle, Loader2 } from "lucide-react";

import { Progress } from "@/components/ui/progress";
import { EXTRACTION_STEPS, extractionStepIndex } from "@/features/resumes/utils";
import type { ResumeStatus } from "@/features/resumes/types";
import { cn } from "@/lib/utils";

interface ExtractionProgressProps {
  status: ResumeStatus;
}

export function ExtractionProgress({ status }: ExtractionProgressProps) {
  if (status === "completed" || status === "failed") return null;

  const activeIndex = extractionStepIndex(status);
  const percent = status === "queued" ? 15 : 55;

  return (
    <div className="space-y-3 rounded-lg border border-primary/20 bg-primary/5 px-3 py-3">
      <div className="flex items-center justify-between text-xs">
        <span className="font-medium text-primary">Extraction in progress</span>
        <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
      </div>
      <Progress value={percent} className="h-1.5" />
      <ol className="space-y-1.5">
        {EXTRACTION_STEPS.map((step, index) => {
          const done = activeIndex > index;
          const active = activeIndex === index;
          return (
            <li
              key={step.label}
              className={cn(
                "flex items-center gap-2 text-xs",
                done && "text-emerald-400",
                active && "font-medium text-amber-400",
                !done && !active && "text-muted-foreground",
              )}
            >
              {done ? (
                <CheckCircle2 className="h-3.5 w-3.5 shrink-0" />
              ) : active ? (
                <Loader2 className="h-3.5 w-3.5 shrink-0 animate-spin" />
              ) : (
                <Circle className="h-3.5 w-3.5 shrink-0 opacity-40" />
              )}
              {step.label}
            </li>
          );
        })}
      </ol>
    </div>
  );
}
