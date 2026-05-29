import type {
  FillerWordStat,
  SessionSpeechSummary,
  SpeechAnalysisResult,
  StructuredSpeechAnalysis,
} from "@/features/speech/types";

export function paceLabel(wpm: number): string {
  if (wpm <= 0) return "Not measured";
  if (wpm < 90) return "Slow";
  if (wpm > 180) return "Fast";
  if (wpm >= 120 && wpm <= 160) return "Ideal";
  return "Moderate";
}

export function toStructuredSpeechAnalysis(
  raw: SpeechAnalysisResult,
  opts?: { role_target?: string | null; question_label?: string | null },
): StructuredSpeechAnalysis {
  const wordCount =
    typeof raw.metrics?.word_count === "number" ? (raw.metrics.word_count as number) : 0;

  const strengths: string[] = [];
  if (raw.fluency_score >= 75) strengths.push("Fluent delivery with few disruptions");
  if (raw.confidence_score >= 75) strengths.push("Confident, assertive language");
  if (raw.speaking_speed_score >= 75) strengths.push("Well-paced speaking speed");
  if (raw.communication_score >= 75 && strengths.length === 0) {
    strengths.push("Clear overall communication");
  }
  if (strengths.length === 0 && raw.communication_score >= 60) {
    strengths.push("Solid foundation — refine pacing and fillers to stand out");
  }

  return {
    version: "phase12",
    role_target: opts?.role_target ?? null,
    question_label: opts?.question_label ?? null,
    scores: {
      communication_score: raw.communication_score,
      fluency_score: raw.fluency_score,
      confidence_score: raw.confidence_score,
      speaking_speed_score: raw.speaking_speed_score,
      pause_score: raw.pause_score,
    },
    delivery: {
      words_per_minute: raw.words_per_minute,
      filler_word_count: raw.filler_word_count,
      pause_count: raw.pause_count,
      hesitation_count: raw.hesitation_count,
      pace_label: paceLabel(raw.words_per_minute),
    },
    skill_radar: {
      Fluency: raw.fluency_score,
      Communication: raw.communication_score,
      Confidence: raw.confidence_score,
      Pace: raw.speaking_speed_score,
      Pauses: raw.pause_score,
    },
    filler_breakdown: raw.filler_word_stats,
    confidence_indicators: raw.confidence_indicators,
    weak_patterns: raw.weak_patterns,
    communication_tips: raw.communication_tips,
    strengths,
    word_count: wordCount,
  };
}

export function toSessionStructuredAnalysis(
  summary: SessionSpeechSummary,
  roleTarget: string,
): StructuredSpeechAnalysis {
  return {
    version: "phase12-session",
    role_target: roleTarget,
    question_label: null,
    scores: {
      communication_score: summary.avg_communication_score,
      fluency_score: summary.avg_fluency_score,
      confidence_score: summary.avg_confidence_score,
      speaking_speed_score: summary.avg_speaking_speed_score,
      pause_score: 0,
    },
    delivery: {
      words_per_minute: summary.avg_words_per_minute,
      filler_word_count: summary.total_filler_words,
      pause_count: 0,
      hesitation_count: 0,
      pace_label: paceLabel(summary.avg_words_per_minute),
    },
    skill_radar: {
      Fluency: summary.avg_fluency_score,
      Communication: summary.avg_communication_score,
      Confidence: summary.avg_confidence_score,
      Pace: summary.avg_speaking_speed_score,
    },
    filler_breakdown: [] as FillerWordStat[],
    confidence_indicators: {},
    weak_patterns: summary.highlight_weak_patterns,
    communication_tips: summary.highlight_tips,
    strengths:
      summary.avg_communication_score >= 70
        ? ["Consistent communication across your interview answers"]
        : ["Complete more practice answers to build a stronger baseline"],
    word_count: 0,
  };
}
