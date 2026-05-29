"use client";

import { motion } from "framer-motion";

import { SpeechAnalysisCharts } from "@/features/speech/components/speech-analysis-charts";
import { SpeechAnalysisScoreHeader } from "@/features/speech/components/speech-analysis-score-header";
import { SpeechAnalysisSections } from "@/features/speech/components/speech-analysis-sections";
import type { StructuredSpeechAnalysis } from "@/features/speech/types";

const reveal = {
  hidden: { opacity: 0, y: 20 },
  show: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.12, duration: 0.45 },
  }),
};

interface SpeechAnalysisResultsProps {
  analysis: StructuredSpeechAnalysis;
  perQuestionScores?: { name: string; communication: number; fluency: number }[];
}

export function SpeechAnalysisResults({
  analysis,
  perQuestionScores,
}: SpeechAnalysisResultsProps) {
  return (
    <div className="space-y-8">
      {(analysis.role_target || analysis.question_label) && (
        <motion.p
          custom={0}
          variants={reveal}
          initial="hidden"
          animate="show"
          className="text-sm text-muted-foreground"
        >
          {analysis.question_label ? (
            <>
              Question <span className="font-medium text-foreground">{analysis.question_label}</span>
              {analysis.role_target ? (
                <>
                  {" "}
                  · Role: <span className="font-medium text-foreground">{analysis.role_target}</span>
                </>
              ) : null}
            </>
          ) : (
            <>
              Evaluated for:{" "}
              <span className="font-medium text-foreground">{analysis.role_target}</span>
            </>
          )}
        </motion.p>
      )}

      <motion.div custom={1} variants={reveal} initial="hidden" animate="show">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Score overview
        </p>
        <SpeechAnalysisScoreHeader analysis={analysis} />
      </motion.div>

      <motion.div custom={2} variants={reveal} initial="hidden" animate="show">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Visual breakdown
        </p>
        <SpeechAnalysisCharts
          analysis={analysis}
          perQuestionScores={perQuestionScores}
        />
      </motion.div>

      <motion.div custom={3} variants={reveal} initial="hidden" animate="show">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Delivery & improvements
        </p>
        <SpeechAnalysisSections analysis={analysis} />
      </motion.div>
    </div>
  );
}
