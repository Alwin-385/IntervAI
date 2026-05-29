"use client";

import { Check } from "lucide-react";

import { cn } from "@/lib/utils";
import { STEP_LABELS } from "@/features/interviews/constants";

interface WizardProgressProps {
  currentStep: number;
  onStepClick?: (step: number) => void;
}

export function WizardProgress({ currentStep, onStepClick }: WizardProgressProps) {
  return (
    <div className="space-y-3">
      <div className="hidden items-center justify-between gap-2 md:flex">
        {STEP_LABELS.map((label, idx) => {
          const done = idx < currentStep;
          const active = idx === currentStep;
          const canJump = done && onStepClick;
          return (
            <div key={label} className="flex flex-1 items-center gap-2">
              <button
                type="button"
                disabled={!canJump && !active}
                onClick={() => canJump && onStepClick(idx)}
                className={cn(
                  "flex h-7 w-7 shrink-0 items-center justify-center rounded-full border text-xs font-medium transition-all",
                  done && "border-primary bg-primary text-primary-foreground",
                  active && "border-primary bg-primary/15 text-primary",
                  !done && !active && "border-border/60 text-muted-foreground",
                  canJump && "cursor-pointer hover:ring-2 hover:ring-primary/40",
                  !canJump && !active && "cursor-default",
                )}
                aria-label={canJump ? `Go back to ${label}` : label}
                aria-current={active ? "step" : undefined}
              >
                {done ? <Check className="h-3.5 w-3.5" /> : idx + 1}
              </button>
              <button
                type="button"
                disabled={!canJump}
                onClick={() => canJump && onStepClick(idx)}
                className={cn(
                  "truncate text-left text-xs font-medium transition-colors",
                  active ? "text-foreground" : "text-muted-foreground",
                  canJump && "cursor-pointer hover:text-foreground",
                )}
              >
                {label}
              </button>
              {idx < STEP_LABELS.length - 1 && (
                <div
                  className={cn(
                    "ml-1 h-px flex-1 transition-colors",
                    done ? "bg-primary/60" : "bg-border/60",
                  )}
                />
              )}
            </div>
          );
        })}
      </div>

      <div className="space-y-2 md:hidden">
        <div className="flex items-center justify-between text-xs">
          <span className="font-medium text-foreground">
            Step {currentStep + 1} of {STEP_LABELS.length}
          </span>
          <span className="text-muted-foreground">
            {STEP_LABELS[currentStep]}
          </span>
        </div>
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
          <div
            className="h-full rounded-full bg-gradient-to-r from-primary to-accent transition-all duration-500"
            style={{
              width: `${((currentStep + 1) / STEP_LABELS.length) * 100}%`,
            }}
          />
        </div>
        {onStepClick && currentStep > 0 && (
          <div className="flex flex-wrap gap-1.5 pt-1">
            {STEP_LABELS.map((label, idx) =>
              idx < currentStep ? (
                <button
                  key={label}
                  type="button"
                  onClick={() => onStepClick(idx)}
                  className="rounded-md border border-primary/30 bg-primary/10 px-2 py-0.5 text-[10px] font-medium text-primary"
                >
                  {label}
                </button>
              ) : null,
            )}
          </div>
        )}
      </div>
    </div>
  );
}
