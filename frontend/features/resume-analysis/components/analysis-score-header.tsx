"use client";

import { motion } from "framer-motion";
import type { StructuredResumeAnalysis } from "@/features/resume-analysis/types";

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
        highlight
          ? "border-primary/40 bg-primary/10"
          : "border-border/50 bg-muted/15"
      }`}
    >
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {label}
      </p>
      <p className={`mt-2 text-3xl font-bold tabular-nums ${highlight ? "text-primary" : ""}`}>
        {Math.round(value)}
        <span className="text-lg font-normal text-muted-foreground">%</span>
      </p>
    </motion.div>
  );
}

interface AnalysisScoreHeaderProps {
  analysis: StructuredResumeAnalysis;
}

export function AnalysisScoreHeader({ analysis }: AnalysisScoreHeaderProps) {
  const { scores } = analysis;
  return (
    <div className="space-y-3">
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <ScoreCard label="ATS score" value={scores.ats_score} delay={0} highlight />
        <ScoreCard label="Role readiness" value={scores.role_readiness_score} delay={0.05} highlight />
        <ScoreCard label="Technical score" value={scores.technical_skill_score} delay={0.1} highlight />
        <ScoreCard label="Project strength" value={scores.project_strength_score} delay={0.15} highlight />
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        <ScoreCard label="Resume quality" value={scores.resume_quality_score} delay={0.2} />
        <ScoreCard label="Communication" value={scores.communication_score} delay={0.25} />
      </div>
    </div>
  );
}
