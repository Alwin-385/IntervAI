import type {
  AnswerEvaluationDetail,
  SessionEvaluationSummary,
  StructuredAnswerEvaluation,
} from "@/features/evaluations/types";

export function toStructuredAnswerEvaluation(
  raw: AnswerEvaluationDetail,
  opts?: { role_target?: string | null; question_label?: string | null },
): StructuredAnswerEvaluation {
  const s = raw.scores;
  return {
    version: "phase13_v2",
    role_target: opts?.role_target ?? null,
    question_label: opts?.question_label ?? null,
    interview_category: raw.interview_category,
    correctness_verdict: raw.correctness_verdict,
    is_correct: raw.is_correct,
    rubric_score: raw.rubric_score,
    rubric_points_matched: raw.rubric_points_matched,
    rubric_points_missed: raw.rubric_points_missed,
    reference_answer: raw.reference_answer,
    correct_answer: raw.correct_answer,
    correctness_explanation: raw.correctness_explanation,
    scores: s,
    skill_radar: {
      Overall: s.overall_score,
      Communication: s.communication_score,
      Technical: s.technical_score,
      Completeness: s.completeness_score,
      Confidence: s.confidence_score,
      Relevance: s.relevance_score,
      Clarity: s.clarity_score,
    },
    summary_feedback: raw.summary_feedback,
    strengths: raw.strengths,
    weaknesses: raw.weaknesses,
    missing_concepts: raw.missing_concepts,
    improved_answer: raw.improved_answer,
    improvement_suggestions: raw.improvement_suggestions,
    technical_feedback: raw.technical_feedback,
    star_feedback: raw.star_feedback,
    dsa_feedback: raw.dsa_feedback,
  };
}

export function toSessionStructuredEvaluation(
  summary: SessionEvaluationSummary,
  targetRole: string | null | undefined,
): StructuredAnswerEvaluation {
  return {
    version: "phase13_v2",
    role_target: targetRole ?? null,
    interview_category: "session",
    correctness_verdict:
      summary.correct_count >= summary.total_questions / 2 ? "correct" : "partially_correct",
    is_correct: summary.correct_count === summary.total_questions && summary.total_questions > 0,
    rubric_score: summary.avg_overall_score,
    rubric_points_matched: [],
    rubric_points_missed: [],
    reference_answer: "",
    correct_answer: "",
    correctness_explanation: summary.marks_display,
    scores: {
      overall_score: summary.avg_overall_score,
      communication_score: summary.avg_communication_score,
      technical_score: summary.avg_technical_score,
      completeness_score: summary.avg_completeness_score,
      confidence_score: summary.avg_confidence_score,
      relevance_score: summary.avg_overall_score,
      clarity_score: summary.avg_communication_score,
      technical_accuracy_score: summary.avg_technical_score,
      professionalism_score: summary.avg_communication_score,
      role_alignment_score: summary.avg_overall_score,
    },
    skill_radar: {
      Overall: summary.avg_overall_score,
      Communication: summary.avg_communication_score,
      Technical: summary.avg_technical_score,
      Completeness: summary.avg_completeness_score,
      Confidence: summary.avg_confidence_score,
    },
    summary_feedback:
      summary.evaluated_count > 0
        ? `Session average across ${summary.evaluated_count} evaluated answer(s).`
        : "No answers were evaluated yet.",
    strengths: summary.highlight_strengths,
    weaknesses: summary.highlight_weaknesses,
    missing_concepts: [],
    improved_answer: "",
    improvement_suggestions: [],
    technical_feedback: null,
    star_feedback: null,
    dsa_feedback: null,
  };
}
