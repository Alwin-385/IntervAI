"use client";

import { DIFFICULTIES } from "@/features/interviews/constants";
import { SelectionCard } from "@/features/interviews/components/selection-card";
import type { InterviewDifficulty } from "@/features/interviews/types";

interface StepDifficultyProps {
  value: InterviewDifficulty | null;
  onChange: (value: InterviewDifficulty) => void;
}

export function StepDifficulty({ value, onChange }: StepDifficultyProps) {
  return (
    <div className="space-y-4">
      <header>
        <h2 className="text-xl font-semibold">How challenging should it feel?</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Difficulty shifts question depth, edge cases, and the bar for a passing answer.
        </p>
      </header>

      <div className="grid gap-3 sm:grid-cols-3">
        {DIFFICULTIES.map((level) => (
          <SelectionCard
            key={level.value}
            icon={level.icon}
            label={level.label}
            blurb={level.blurb}
            active={value === level.value}
            accent={level.accent}
            onSelect={() => onChange(level.value)}
          />
        ))}
      </div>
    </div>
  );
}
