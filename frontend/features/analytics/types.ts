export type TrendDirection = "improving" | "declining" | "stable" | "insufficient_data";

export interface AnalyticsFiltersApplied {
  target_role: string | null;
  category: string | null;
  days: number | null;
}

export interface AnalyticsSummary {
  total_interviews: number;
  completed_interviews: number;
  total_answers_evaluated: number;
  average_score: number | null;
  average_communication: number | null;
  average_confidence: number | null;
  average_technical: number | null;
  improvement_score: number | null;
  score_trend: TrendDirection;
  score_trend_delta: number;
}

export interface ScoreTrendPoint {
  label: string;
  date: string;
  session_id: string | null;
  average_score: number;
  target_role: string | null;
  category: string | null;
}

export interface MetricTrendPoint {
  label: string;
  date: string;
  value: number;
}

export interface InterviewHistoryItem {
  session_id: string;
  title: string;
  target_role: string;
  category: string;
  status: string;
  difficulty: string;
  completed_at: string | null;
  created_at: string;
  question_count: number;
  answered_count: number;
  average_score: number | null;
  communication_score: number | null;
  confidence_score: number | null;
  technical_score: number | null;
  correctness_rate: number | null;
}

export interface WeakAreaFrequencyItem {
  kind: string;
  area_name: string;
  frequency: number;
  frequency_rate: number;
  priority: string;
}

export interface RoleReadinessItem {
  target_role: string;
  readiness_score: number;
  interviews_completed: number;
  average_score: number | null;
  trend: TrendDirection;
}

export interface ImprovementProgressSnapshot {
  roadmap_completion_rate: number;
  roadmap_items_completed: number;
  roadmap_items_total: number;
  weak_areas_high_priority: number;
  weak_areas_improving: number;
  weak_areas_declining: number;
  overall_improvement_score: number | null;
}

export interface AnalyticsDashboard {
  version: string;
  generated_at: string;
  filters_applied: AnalyticsFiltersApplied;
  available_roles: string[];
  available_categories: string[];
  summary: AnalyticsSummary;
  score_over_time: ScoreTrendPoint[];
  communication_trend: MetricTrendPoint[];
  confidence_trend: MetricTrendPoint[];
  technical_trend: MetricTrendPoint[];
  interview_history: InterviewHistoryItem[];
  interview_history_total: number;
  interview_history_page: number;
  interview_history_page_size: number;
  interview_history_pages: number;
  weak_area_frequency: WeakAreaFrequencyItem[];
  role_readiness: RoleReadinessItem[];
  improvement_progress: ImprovementProgressSnapshot;
}

export interface AnalyticsProgress {
  version: string;
  generated_at: string;
  filters_applied: AnalyticsFiltersApplied;
  improvement_score_over_time: MetricTrendPoint[];
  correctness_over_time: MetricTrendPoint[];
  roadmap_completion_over_time: MetricTrendPoint[];
  improvement_progress: ImprovementProgressSnapshot;
}

export interface AnalyticsDashboardParams {
  page?: number;
  page_size?: number;
  target_role?: string;
  category?: string;
  days?: number;
}
