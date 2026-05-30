"use client";

import { motion } from "framer-motion";
import { CheckCircle2, HelpCircle, XCircle } from "lucide-react";

import type { SessionEvaluationSummary } from "@/features/evaluations/types";
import { cn } from "@/lib/utils";

interface EvaluationMarksBannerProps {
  summary: SessionEvaluationSummary;
  className?: string;
}

export function EvaluationMarksBanner({ summary, className }: EvaluationMarksBannerProps) {
  const {
    marks_display,
    correct_count,
    partially_correct_count,
    incorrect_count,
    total_questions,
  } = summary;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn("rounded-2xl border border-primary/30 bg-primary/5 p-5 md:p-6", className)}
    >
      <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        Interview score
      </p>
      <p className="mt-2 text-4xl font-bold tabular-nums tracking-tight text-primary">
        {marks_display}
      </p>
      <p className="mt-1 text-sm text-muted-foreground">
        Based on rubric match to expected answer points from your interview questions
        {summary.answered_count < total_questions
          ? ` · ${summary.answered_count}/${total_questions} answered`
          : null}
      </p>
      <div className="mt-4 flex flex-wrap gap-3 text-sm">
        <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/15 px-3 py-1 text-emerald-700 dark:text-emerald-300">
          <CheckCircle2 className="h-4 w-4" />
          {correct_count} correct
        </span>
        {partially_correct_count > 0 && (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-500/15 px-3 py-1 text-amber-800 dark:text-amber-200">
            <HelpCircle className="h-4 w-4" />
            {partially_correct_count} partial
          </span>
        )}
        {incorrect_count > 0 && (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-red-500/15 px-3 py-1 text-red-700 dark:text-red-300">
            <XCircle className="h-4 w-4" />
            {incorrect_count} incorrect
          </span>
        )}
      </div>
    </motion.div>
  );
}
