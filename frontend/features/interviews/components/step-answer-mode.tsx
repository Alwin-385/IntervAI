"use client";

import { ANSWER_MODES } from "@/features/interviews/constants";
import { SelectionCard } from "@/features/interviews/components/selection-card";
import type { AnswerMode } from "@/features/interviews/types";

interface StepAnswerModeProps {
  value: AnswerMode | null;
  onChange: (value: AnswerMode) => void;
}

export function StepAnswerMode({ value, onChange }: StepAnswerModeProps) {
  return (
    <div className="space-y-4">
      <header>
        <h2 className="text-xl font-semibold">How will you answer?</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Voice mode adds speech feedback (pace, filler words). You can switch later.
        </p>
      </header>

      <div className="grid gap-3 sm:grid-cols-2">
        {ANSWER_MODES.map((mode) => (
          <SelectionCard
            key={mode.value}
            icon={mode.icon}
            label={mode.label}
            blurb={mode.blurb}
            active={value === mode.value}
            onSelect={() => onChange(mode.value)}
          />
        ))}
      </div>
    </div>
  );
}
