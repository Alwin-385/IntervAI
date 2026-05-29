"use client";

import { useState } from "react";
import { Hash } from "lucide-react";

import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";
import {
  MAX_QUESTIONS,
  MIN_QUESTIONS,
  QUESTION_COUNT_PRESETS,
} from "@/features/interviews/constants";

interface StepQuestionCountProps {
  value: number;
  onChange: (value: number) => void;
}

export function StepQuestionCount({ value, onChange }: StepQuestionCountProps) {
  const [custom, setCustom] = useState<string>(
    QUESTION_COUNT_PRESETS.includes(value as (typeof QUESTION_COUNT_PRESETS)[number])
      ? ""
      : String(value),
  );

  return (
    <div className="space-y-5">
      <header>
        <h2 className="text-xl font-semibold">How many questions?</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Pick a length that fits your time. Most users prefer 8–10 questions for a focused session.
        </p>
      </header>

      <div className="flex flex-wrap gap-3">
        {QUESTION_COUNT_PRESETS.map((preset) => {
          const active = value === preset && !custom;
          return (
            <button
              key={preset}
              type="button"
              onClick={() => {
                setCustom("");
                onChange(preset);
              }}
              className={cn(
                "flex h-20 w-20 flex-col items-center justify-center rounded-2xl border transition-all",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary",
                active
                  ? "border-primary bg-primary/10 text-primary shadow-lg shadow-primary/10"
                  : "border-border/60 bg-card/60 text-foreground hover:border-primary/40 hover:bg-primary/5",
              )}
            >
              <span className="text-2xl font-bold leading-none">{preset}</span>
              <span className="mt-1 text-[10px] uppercase tracking-wide text-muted-foreground">
                questions
              </span>
            </button>
          );
        })}
      </div>

      <div className="rounded-xl border border-border/60 bg-card/60 p-4">
        <label
          htmlFor="custom-count"
          className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-muted-foreground"
        >
          <Hash className="h-3 w-3" />
          Or pick a custom amount ({MIN_QUESTIONS}–{MAX_QUESTIONS})
        </label>
        <Input
          id="custom-count"
          type="number"
          min={MIN_QUESTIONS}
          max={MAX_QUESTIONS}
          value={custom}
          placeholder="e.g. 12"
          onChange={(e) => {
            const raw = e.target.value;
            setCustom(raw);
            const parsed = Number(raw);
            if (!Number.isNaN(parsed) && parsed >= MIN_QUESTIONS && parsed <= MAX_QUESTIONS) {
              onChange(parsed);
            }
          }}
          className="max-w-[160px]"
        />
      </div>
    </div>
  );
}
