"use client";

import { motion } from "framer-motion";

import type { StructuredAnswerEvaluation } from "@/features/evaluations/types";

interface ScoreCardProps {
  label: string;
  value: number;
  delay?: number;
  highlight?: boolean;
}

function ScoreCard({ label, value, delay = 0, highlight }: ScoreCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className={`rounded-xl border p-4 ${
        highlight ? "border-primary/40 bg-primary/10" : "border-border/50 bg-muted/15"
      }`}
    >
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className={`mt-2 text-3xl font-bold tabular-nums ${highlight ? "text-primary" : ""}`}>
        {Math.round(value)}
        <span className="text-lg font-normal text-muted-foreground"> %</span>
      </p>
    </motion.div>
  );
}

interface AnswerEvaluationScoreHeaderProps {
  analysis: StructuredAnswerEvaluation;
}

export function AnswerEvaluationScoreHeader({ analysis }: AnswerEvaluationScoreHeaderProps) {
  const { scores } = analysis;
  return (
    <div className="space-y-3">
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <ScoreCard label="Overall" value={scores.overall_score} delay={0} highlight />
        <ScoreCard
          label="Communication"
          value={scores.communication_score}
          delay={0.05}
          highlight
        />
        <ScoreCard label="Technical" value={scores.technical_score} delay={0.1} highlight />
        <ScoreCard label="Completeness" value={scores.completeness_score} delay={0.15} highlight />
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <ScoreCard label="Confidence" value={scores.confidence_score} delay={0.2} />
        <ScoreCard label="Relevance" value={scores.relevance_score} delay={0.25} />
        <ScoreCard label="Clarity" value={scores.clarity_score} delay={0.3} />
        <ScoreCard label="Role alignment" value={scores.role_alignment_score} delay={0.35} />
      </div>
    </div>
  );
}
