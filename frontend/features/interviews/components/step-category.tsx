"use client";

import { CATEGORIES } from "@/features/interviews/constants";
import { SelectionCard } from "@/features/interviews/components/selection-card";
import type { InterviewCategory } from "@/features/interviews/types";

interface StepCategoryProps {
  value: InterviewCategory | null;
  onChange: (value: InterviewCategory) => void;
}

export function StepCategory({ value, onChange }: StepCategoryProps) {
  return (
    <div className="space-y-4">
      <header>
        <h2 className="text-xl font-semibold">What kind of interview?</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Choose a focus area. Resume-Based pulls from your uploaded resume; Mixed blends all categories.
        </p>
      </header>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {CATEGORIES.map((cat) => (
          <SelectionCard
            key={cat.value}
            icon={cat.icon}
            label={cat.label}
            blurb={cat.blurb}
            active={value === cat.value}
            onSelect={() => onChange(cat.value)}
          />
        ))}
      </div>
    </div>
  );
}
