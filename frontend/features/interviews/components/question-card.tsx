"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { ChevronDown, Clock, Target } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { InterviewQuestionDetail } from "@/features/interviews/types";
import {
  categoryLabel,
  difficultyLabel,
  formatTimeLimit,
} from "@/features/interviews/utils";

interface QuestionCardProps {
  question: InterviewQuestionDetail;
  index: number;
}

export function QuestionCard({ question, index }: QuestionCardProps) {
  const [open, setOpen] = useState(false);

  return (
    <motion.article
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04, duration: 0.25 }}
      className="glass-card overflow-hidden rounded-2xl border border-border/60"
    >
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-start gap-4 p-5 text-left transition-colors hover:bg-muted/20"
      >
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/15 text-sm font-bold text-primary">
          {index + 1}
        </div>
        <div className="min-w-0 flex-1">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <Badge variant="secondary" className="border-primary/30 bg-primary/10 text-primary">
              {categoryLabel(question.category)}
            </Badge>
            <Badge variant="outline" className={difficultyBadgeClass(question.difficulty)}>
              {difficultyLabel(question.difficulty)}
            </Badge>
            {question.time_limit_seconds != null && (
              <Badge variant="outline" className="gap-1 border-border/60 text-muted-foreground">
                <Clock className="h-3 w-3" />
                {formatTimeLimit(question.time_limit_seconds)}
              </Badge>
            )}
          </div>
          <p className="text-sm font-medium leading-relaxed text-foreground">
            {question.question_text}
          </p>
          {question.source_hint && (
            <p className="mt-2 flex items-center gap-1 text-xs text-muted-foreground">
              <Target className="h-3 w-3 shrink-0 text-primary" />
              Resume focus: {question.source_hint}
            </p>
          )}
        </div>
        <ChevronDown
          className={cn(
            "mt-1 h-5 w-5 shrink-0 text-muted-foreground transition-transform",
            open && "rotate-180",
          )}
        />
      </button>

      {open && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          className="border-t border-border/50 bg-muted/10 px-5 py-4"
        >
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Expected answer points
              </p>
              <ul className="list-inside list-disc space-y-1 text-sm text-foreground/90">
                {question.expected_answer_points.map((pt) => (
                  <li key={pt}>{pt}</li>
                ))}
              </ul>
            </div>
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Evaluation criteria
              </p>
              <ul className="list-inside list-disc space-y-1 text-sm text-foreground/90">
                {question.evaluation_criteria.map((c) => (
                  <li key={c}>{c}</li>
                ))}
              </ul>
            </div>
          </div>
        </motion.div>
      )}
    </motion.article>
  );
}

function difficultyBadgeClass(difficulty: string): string {
  switch (difficulty) {
    case "beginner":
      return "border-emerald-500/40 bg-emerald-500/10 text-emerald-400";
    case "advanced":
      return "border-rose-500/40 bg-rose-500/10 text-rose-400";
    default:
      return "border-amber-500/40 bg-amber-500/10 text-amber-400";
  }
}
