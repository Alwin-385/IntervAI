import type { SpeechAnalysisResult } from "@/features/speech/types";

export function isSpeechAnalysisComplete(
  analysis: SpeechAnalysisResult | null | undefined,
): boolean {
  if (!analysis) return false;
  const chart = analysis.metrics?.chart_scores as Record<string, number> | undefined;
  if (chart && typeof chart.fluency === "number" && chart.fluency > 0) {
    return true;
  }
  const wordCount =
    typeof analysis.metrics?.word_count === "number" ? (analysis.metrics.word_count as number) : 0;
  return analysis.communication_score > 0 && wordCount > 0;
}
