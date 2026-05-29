export type CorrectnessVerdict = "correct" | "partially_correct" | "incorrect";

export interface AnswerScoreBreakdown {
  overall_score: number;
  communication_score: number;
  technical_score: number;
  completeness_score: number;
  confidence_score: number;
  relevance_score: number;
  clarity_score: number;
  technical_accuracy_score: number;
  professionalism_score: number;
  role_alignment_score: number;
}

export interface StarMethodFeedback {
  situation_score: number;
  task_score: number;
  action_score: number;
  result_score: number;
  overall_star_score: number;
  feedback: string;
  missing_elements: string[];
  improved_star_outline: string;
}

export interface DsaComplexityFeedback {
  time_complexity: string;
  space_complexity: string;
  correctness_score: number;
  optimality_score: number;
  feedback: string;
  suggested_improvements: string[];
}

export interface AnswerEvaluationDetail {
  id: string;
  answer_id: string;
  question_id: string;
  session_id: string;
  question_text: string;
  answer_preview: string;
  interview_category: string;
  scores: AnswerScoreBreakdown;
  correctness_verdict: CorrectnessVerdict;
  is_correct: boolean;
  rubric_score: number;
  rubric_points_matched: string[];
  rubric_points_missed: string[];
  reference_answer: string;
  correct_answer: string;
  correctness_explanation: string;
  summary_feedback: string;
  strengths: string[];
  weaknesses: string[];
  missing_concepts: string[];
  improved_answer: string;
  improvement_suggestions: string[];
  technical_feedback: string | null;
  star_feedback: StarMethodFeedback | null;
  dsa_feedback: DsaComplexityFeedback | null;
}

export interface SessionEvaluationSummary {
  total_questions: number;
  answered_count: number;
  evaluated_count: number;
  skipped_count: number;
  correct_count: number;
  partially_correct_count: number;
  incorrect_count: number;
  marks_obtained: number;
  marks_display: string;
  avg_overall_score: number;
  avg_communication_score: number;
  avg_technical_score: number;
  avg_completeness_score: number;
  avg_confidence_score: number;
  highlight_strengths: string[];
  highlight_weaknesses: string[];
}

export interface QuestionAnswerEvaluation {
  question_id: string;
  question_text: string;
  order_index: number;
  answer_id: string | null;
  answer_preview: string;
  evaluation: AnswerEvaluationDetail | null;
}

export interface SessionAnswerEvaluationResults {
  session_id: string;
  session_title: string | null;
  target_role: string | null;
  questions: QuestionAnswerEvaluation[];
  summary: SessionEvaluationSummary;
}

/** UI-normalized shape (mirrors speech StructuredSpeechAnalysis). */
export interface StructuredAnswerEvaluation {
  version: string;
  role_target?: string | null;
  question_label?: string | null;
  interview_category: string;
  correctness_verdict: CorrectnessVerdict;
  is_correct: boolean;
  rubric_score: number;
  rubric_points_matched: string[];
  rubric_points_missed: string[];
  reference_answer: string;
  correct_answer: string;
  correctness_explanation: string;
  scores: AnswerScoreBreakdown;
  skill_radar: Record<string, number>;
  summary_feedback: string;
  strengths: string[];
  weaknesses: string[];
  missing_concepts: string[];
  improved_answer: string;
  improvement_suggestions: string[];
  technical_feedback: string | null;
  star_feedback: StarMethodFeedback | null;
  dsa_feedback: DsaComplexityFeedback | null;
}
