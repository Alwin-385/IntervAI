/**
 * Type-level sanity tests for analytics types (runtime shape checks).
 */

import type {
  AnalyticsDashboard,
  AnalyticsSummary,
  TrendDirection,
} from "@/features/analytics/types";

describe("AnalyticsSummary shape", () => {
  const summary: AnalyticsSummary = {
    total_interviews: 5,
    completed_interviews: 4,
    total_answers_evaluated: 20,
    average_score: 0.72,
    average_communication: 0.68,
    average_confidence: 0.75,
    average_technical: 0.7,
    improvement_score: 0.15,
    score_trend: "improving",
    score_trend_delta: 0.12,
  };

  it("has all required fields", () => {
    expect(summary.total_interviews).toBeDefined();
    expect(summary.score_trend).toBeDefined();
  });

  it("accepts all TrendDirection values", () => {
    const directions: TrendDirection[] = ["improving", "declining", "stable", "insufficient_data"];
    directions.forEach((d) => {
      expect(typeof d).toBe("string");
    });
  });
});

describe("AnalyticsDashboard", () => {
  it("can be constructed with required fields", () => {
    const dashboard: AnalyticsDashboard = {
      version: "1",
      generated_at: new Date().toISOString(),
      filters_applied: { target_role: null, category: null, days: null },
      available_roles: [],
      available_categories: [],
      summary: {
        total_interviews: 0,
        completed_interviews: 0,
        total_answers_evaluated: 0,
        average_score: null,
        average_communication: null,
        average_confidence: null,
        average_technical: null,
        improvement_score: null,
        score_trend: "insufficient_data",
        score_trend_delta: 0,
      },
      score_over_time: [],
      communication_trend: [],
      confidence_trend: [],
      technical_trend: [],
      interview_history: [],
      interview_history_total: 0,
      interview_history_page: 1,
      interview_history_page_size: 10,
      interview_history_pages: 0,
      weak_area_frequency: [],
      role_readiness: [],
      improvement_progress: {
        roadmap_completion_rate: 0,
        roadmap_items_completed: 0,
        roadmap_items_total: 0,
        weak_areas_high_priority: 0,
        weak_areas_improving: 0,
        weak_areas_declining: 0,
        overall_improvement_score: null,
      },
    };

    expect(dashboard.version).toBe("1");
    expect(Array.isArray(dashboard.interview_history)).toBe(true);
  });
});
