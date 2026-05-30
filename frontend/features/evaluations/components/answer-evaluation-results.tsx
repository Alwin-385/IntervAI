"use client";

import { motion } from "framer-motion";

import { AnswerEvaluationCharts } from "@/features/evaluations/components/answer-evaluation-charts";
import { AnswerEvaluationScoreHeader } from "@/features/evaluations/components/answer-evaluation-score-header";
import { AnswerEvaluationSections } from "@/features/evaluations/components/answer-evaluation-sections";
import { CorrectnessBadge } from "@/features/evaluations/components/correctness-badge";
import type { StructuredAnswerEvaluation } from "@/features/evaluations/types";

const reveal = {
  hidden: { opacity: 0, y: 20 },
  show: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.12, duration: 0.45 },
  }),
};

interface AnswerEvaluationResultsProps {
  analysis: StructuredAnswerEvaluation;
  perQuestionScores?: { name: string; overall: number; technical: number }[];
}

export function AnswerEvaluationResults({
  analysis,
  perQuestionScores,
}: AnswerEvaluationResultsProps) {
  const categoryLabel = analysis.interview_category.replace(/_/g, " ");

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
              Question{" "}
              <span className="font-medium text-foreground">{analysis.question_label}</span>
              {analysis.role_target ? (
                <>
                  {" "}
                  · Role:{" "}
                  <span className="font-medium text-foreground">{analysis.role_target}</span>
                </>
              ) : null}
            </>
          ) : (
            <>
              Evaluated for{" "}
              <span className="font-medium text-foreground">{analysis.role_target}</span>
              {categoryLabel !== "session" && (
                <>
                  {" "}
                  · <span className="capitalize">{categoryLabel}</span> interview
                </>
              )}
            </>
          )}
        </motion.p>
      )}

      <motion.div
        custom={1}
        variants={reveal}
        initial="hidden"
        animate="show"
        className="space-y-4"
      >
        <div className="flex flex-wrap items-center gap-3">
          <CorrectnessBadge verdict={analysis.correctness_verdict} />
          <span className="text-sm text-muted-foreground">
            Rubric match:{" "}
            <span className="font-medium text-foreground">
              {Math.round(analysis.rubric_score)}%
            </span>
          </span>
        </div>
        {analysis.correctness_explanation && (
          <p className="text-sm leading-relaxed text-muted-foreground">
            {analysis.correctness_explanation}
          </p>
        )}
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Score overview
        </p>
        <AnswerEvaluationScoreHeader analysis={analysis} />
      </motion.div>

      <motion.div custom={2} variants={reveal} initial="hidden" animate="show">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Visual breakdown
        </p>
        <AnswerEvaluationCharts analysis={analysis} perQuestionScores={perQuestionScores} />
      </motion.div>

      <motion.div custom={3} variants={reveal} initial="hidden" animate="show">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Interviewer feedback
        </p>
        <AnswerEvaluationSections analysis={analysis} />
      </motion.div>
    </div>
  );
}
