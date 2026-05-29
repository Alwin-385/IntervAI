export type WeakAreaPriority = "high" | "medium" | "low";
export type WeakAreaTrend = "improving" | "declining" | "stable" | "insufficient_data";
export type WeakAreaSeverity = "low" | "medium" | "high" | "critical";

export interface DetectedWeakArea {
  kind: string;
  area_name: string;
  category: string;
  priority: WeakAreaPriority;
  severity: WeakAreaSeverity;
  frequency: number;
  total_opportunities: number;
  frequency_rate: number;
  frequency_label: string;
  trend: WeakAreaTrend;
  trend_delta: number;
  description: string;
  improvement_suggestions: string[];
  practice_recommendations: string[];
  evidence: string[];
  last_seen_at: string | null;
}

export interface WeakAreaTrendPoint {
  period_label: string;
  hit_count: number;
  opportunity_count: number;
  rate: number;
}

export interface WeakAreaProgressSummary {
  interviews_analyzed: number;
  answers_analyzed: number;
  speech_analyses_analyzed: number;
  overall_improvement_score: number;
  high_priority_count: number;
  medium_priority_count: number;
  low_priority_count: number;
}

export interface WeakAreasAnalytics {
  version: string;
  generated_at: string;
  weak_areas: DetectedWeakArea[];
  summary: WeakAreaProgressSummary;
  personalized_recommendations: string[];
  trend_overview: WeakAreaTrendPoint[];
}
