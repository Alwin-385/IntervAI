"use client";

import { Loader2 } from "lucide-react";

import { SpeechAnalysisResults } from "@/features/speech/components/speech-analysis-results";
import { useSpeechSessionResults } from "@/features/speech/hooks/use-speech-session-results";
import {
  toSessionStructuredAnalysis,
  toStructuredSpeechAnalysis,
} from "@/features/speech/utils/speech-analysis-mapper";
import { cn } from "@/lib/utils";

interface SpeechSessionResultsProps {
  sessionId: string;
  className?: string;
}

export function SpeechSessionResults({ sessionId, className }: SpeechSessionResultsProps) {
  const { data, isLoading, isError, error, isFetching } = useSpeechSessionResults(sessionId);

  if (isLoading || (isFetching && !data)) {
    return (
      <div
        className={cn(
          "glass-card flex flex-col items-center gap-3 rounded-2xl border p-10",
          className,
        )}
      >
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-sm text-muted-foreground">Analyzing your communication…</p>
        <p className="text-xs text-muted-foreground">Pace, fillers, fluency, and confidence</p>
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
        {error instanceof Error ? error.message : "Could not load speech results"}
      </div>
    );
  }

  const answered = data.questions.filter((q) => q.analysis);
  const sessionAnalysis = toSessionStructuredAnalysis(data.summary, data.target_role);

  const perQuestionChart = answered.map((q) => ({
    name: `Q${q.order_index + 1}`,
    communication: q.analysis?.communication_score ?? 0,
    fluency: q.analysis?.fluency_score ?? 0,
  }));

  return (
    <div className={cn("space-y-12", className)}>
      <SpeechAnalysisResults
        analysis={sessionAnalysis}
        perQuestionScores={perQuestionChart.length > 1 ? perQuestionChart : undefined}
      />

      {answered.length > 0 && (
        <div className="space-y-8 border-t border-border/60 pt-10">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Per-question breakdown
          </p>
          {answered.map((item) => {
            if (!item.analysis) return null;
            const structured = toStructuredSpeechAnalysis(item.analysis, {
              role_target: data.target_role,
              question_label: String(item.order_index + 1),
            });
            return (
              <div key={item.question_id} className="space-y-2">
                <p className="line-clamp-2 text-sm font-medium text-foreground">
                  {item.question_text}
                </p>
                <SpeechAnalysisResults analysis={structured} />
              </div>
            );
          })}
        </div>
      )}

      {answered.length === 0 && (
        <p className="text-sm text-muted-foreground">
          No answers with text were found. Record voice answers in Chrome or Edge (speak while the
          mic is on), or type your responses — then complete the interview again to analyze.
        </p>
      )}
    </div>
  );
}
