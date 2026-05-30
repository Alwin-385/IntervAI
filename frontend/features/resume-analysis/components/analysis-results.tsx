"use client";

import { motion } from "framer-motion";

import { AnalysisCharts } from "@/features/resume-analysis/components/analysis-charts";
import { AnalysisScoreHeader } from "@/features/resume-analysis/components/analysis-score-header";
import { AnalysisSections } from "@/features/resume-analysis/components/analysis-sections";
import type { StructuredResumeAnalysis } from "@/features/resume-analysis/types";

const reveal = {
  hidden: { opacity: 0, y: 20 },
  show: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.12, duration: 0.45 },
  }),
};

interface AnalysisResultsProps {
  analysis: StructuredResumeAnalysis;
}

export function AnalysisResults({ analysis }: AnalysisResultsProps) {
  return (
    <div className="space-y-8">
      {analysis.role_target && (
        <motion.p
          custom={0}
          variants={reveal}
          initial="hidden"
          animate="show"
          className="text-sm text-muted-foreground"
        >
          Evaluated for: <span className="font-medium text-foreground">{analysis.role_target}</span>
        </motion.p>
      )}

      <motion.div custom={1} variants={reveal} initial="hidden" animate="show">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Score overview
        </p>
        <AnalysisScoreHeader analysis={analysis} />
      </motion.div>

      <motion.div custom={2} variants={reveal} initial="hidden" animate="show">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Visual breakdown
        </p>
        <AnalysisCharts analysis={analysis} />
      </motion.div>

      <motion.div custom={3} variants={reveal} initial="hidden" animate="show">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Profile & improvements
        </p>
        <AnalysisSections analysis={analysis} />
      </motion.div>
    </div>
  );
}
