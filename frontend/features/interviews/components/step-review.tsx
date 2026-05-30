"use client";

import { useMemo } from "react";
import { Briefcase, FileText, Layers, Mic, Pencil, Target } from "lucide-react";

import { ANSWER_MODES, CATEGORIES, DIFFICULTIES } from "@/features/interviews/constants";
import type { InterviewWizardState } from "@/features/interviews/types";

interface StepReviewProps {
  state: InterviewWizardState;
  resumeTitle?: string | null;
}

export function StepReview({ state, resumeTitle }: StepReviewProps) {
  const category = useMemo(
    () => CATEGORIES.find((c) => c.value === state.category),
    [state.category],
  );
  const difficulty = useMemo(
    () => DIFFICULTIES.find((d) => d.value === state.difficulty),
    [state.difficulty],
  );
  const answerMode = useMemo(
    () => ANSWER_MODES.find((a) => a.value === state.answer_mode),
    [state.answer_mode],
  );

  const rows: { icon: typeof Briefcase; label: string; value: string }[] = [
    { icon: Briefcase, label: "Target role", value: state.target_role || "—" },
    {
      icon: category?.icon ?? Layers,
      label: "Category",
      value: category?.label ?? "—",
    },
    {
      icon: difficulty?.icon ?? Target,
      label: "Difficulty",
      value: difficulty?.label ?? "—",
    },
    {
      icon: Layers,
      label: "Questions",
      value: `${state.question_count} questions`,
    },
    {
      icon: answerMode?.icon ?? (answerMode?.value === "voice" ? Mic : Pencil),
      label: "Answer mode",
      value: answerMode?.label ?? "—",
    },
  ];

  if (state.category === "resume_based") {
    rows.push({
      icon: FileText,
      label: "Resume",
      value: resumeTitle ?? "Latest resume",
    });
  }

  return (
    <div className="space-y-4">
      <header>
        <h2 className="text-xl font-semibold">Review your setup</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Looks good? Hit <strong>Create interview</strong> to spin up your session.
        </p>
      </header>

      <div className="overflow-hidden rounded-2xl border border-border/60 bg-card/60">
        <ul className="divide-y divide-border/50">
          {rows.map(({ icon: Icon, label, value }) => (
            <li key={label} className="flex items-center gap-4 px-5 py-3.5 text-sm">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Icon className="h-4 w-4" />
              </div>
              <div className="flex-1">
                <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  {label}
                </p>
                <p className="text-sm font-medium text-foreground">{value}</p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
