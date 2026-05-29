"use client";

import { Loader2 } from "lucide-react";

import { AnswerEvaluationResults } from "@/features/evaluations/components/answer-evaluation-results";
import { EvaluationMarksBanner } from "@/features/evaluations/components/evaluation-marks-banner";
import { useEvaluationSessionResults } from "@/features/evaluations/hooks/use-evaluation-session-results";
import { useSpeechSessionResults } from "@/features/speech/hooks/use-speech-session-results";
import {
  toSessionStructuredEvaluation,
  toStructuredAnswerEvaluation,
} from "@/features/evaluations/utils/evaluation-mapper";
import { cn } from "@/lib/utils";

interface EvaluationSessionResultsProps {
  sessionId: string;
  className?: string;
}

export function EvaluationSessionResults({ sessionId, className }: EvaluationSessionResultsProps) {
  const speechQuery = useSpeechSessionResults(sessionId);
  const speechReady = speechQuery.isSuccess || speechQuery.isError;

  const { data, isLoading, isError, error, isFetching } = useEvaluationSessionResults(sessionId, {
    enabled: speechReady,
  });

  if (!speechReady || isLoading || (isFetching && !data)) {
    return (
      <div
        className={cn(
          "glass-card flex flex-col items-center gap-3 rounded-2xl border p-10",
          className,
        )}
      >
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-sm text-muted-foreground">
          {!speechReady ? "Analyzing delivery first…" : "Evaluating your answers…"}
        </p>
        <p className="text-xs text-muted-foreground">
          Rubric correctness, marks, and reference answers
        </p>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div
        className={cn(
          "rounded-xl border border-destructive/30 bg-destructive/10 p-4 text-sm",
          className,
        )}
      >
        {error instanceof Error ? error.message : "Could not load answer evaluations"}
      </div>
    );
  }

  const evaluated = data.questions.filter((q) => q.evaluation);
  const sessionAnalysis = toSessionStructuredEvaluation(data.summary, data.target_role);

  const perQuestionChart = evaluated.map((q) => ({
    name: `Q${q.order_index + 1}`,
    overall: q.evaluation?.scores.overall_score ?? 0,
    technical: q.evaluation?.scores.technical_score ?? 0,
  }));

  return (
    <div className={cn("space-y-12", className)}>
      {data.summary.total_questions > 0 && (
        <EvaluationMarksBanner summary={data.summary} />
      )}

      <AnswerEvaluationResults
        analysis={sessionAnalysis}
        perQuestionScores={perQuestionChart.length > 1 ? perQuestionChart : undefined}
      />

      {evaluated.length > 0 && (
        <div className="space-y-8 border-t border-border/60 pt-10">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Per-question feedback
          </p>
          {evaluated.map((item) => {
            if (!item.evaluation) return null;
            const structured = toStructuredAnswerEvaluation(item.evaluation, {
              role_target: data.target_role,
              question_label: String(item.order_index + 1),
            });
            return (
              <div key={item.question_id} className="space-y-3 rounded-xl border border-border/40 p-4">
                <p className="line-clamp-2 text-sm font-medium text-foreground">
                  Q{item.order_index + 1}: {item.question_text}
                </p>
                <AnswerEvaluationResults analysis={structured} />
              </div>
            );
          })}
        </div>
      )}

      {evaluated.length === 0 && (
        <p className="text-sm text-muted-foreground">
          No text answers to evaluate. Type or record voice answers (with transcript), then return
          here after completing the interview.
        </p>
      )}
    </div>
  );
}
