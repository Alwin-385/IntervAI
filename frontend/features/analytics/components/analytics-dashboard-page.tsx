"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { BarChart3, Loader2 } from "lucide-react";

import {
  AnalyticsFilters,
  type AnalyticsFilterState,
} from "@/features/analytics/components/analytics-filters";
import { AnalyticsSummaryCards } from "@/features/analytics/components/analytics-summary-cards";
import { ImprovementProgressPanel } from "@/features/analytics/components/improvement-progress-panel";
import { InterviewHistoryChart } from "@/features/analytics/components/interview-history-chart";
import { InterviewHistoryTable } from "@/features/analytics/components/interview-history-table";
import { MetricTrendChart } from "@/features/analytics/components/metric-trend-chart";
import { RoleReadinessPanel } from "@/features/analytics/components/role-readiness-panel";
import { ScoreTrendChart } from "@/features/analytics/components/score-trend-chart";
import { WeakAreaFrequencyChart } from "@/features/analytics/components/weak-area-frequency-chart";
import {
  useAnalyticsDashboard,
  useAnalyticsProgress,
} from "@/features/analytics/hooks/use-analytics-dashboard";

export function AnalyticsDashboardPage() {
  const [filters, setFilters] = useState<AnalyticsFilterState>({ page: 1 });

  const { data, isLoading, isError, error } = useAnalyticsDashboard({
    page: filters.page,
    page_size: 10,
    target_role: filters.target_role,
    category: filters.category,
    days: filters.days,
  });

  const { data: progress } = useAnalyticsProgress({
    target_role: filters.target_role,
    category: filters.category,
    days: filters.days,
  });

  function updateFilters(next: Partial<AnalyticsFilterState>) {
    setFilters((prev) => ({ ...prev, ...next }));
  }

  if (isLoading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <p className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
        {(error as Error)?.message ?? "Failed to load analytics"}
      </p>
    );
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="flex items-center gap-2 text-2xl font-bold">
          <BarChart3 className="h-7 w-7 text-primary" />
          Analytics Dashboard
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          AI-powered interview performance, trends, and improvement tracking
        </p>
      </motion.div>

      <div className="grid gap-6 lg:grid-cols-4">
        <div className="lg:col-span-1">
          <AnalyticsFilters
            filters={filters}
            availableRoles={data.available_roles}
            availableCategories={data.available_categories}
            onChange={updateFilters}
          />
        </div>

        <div className="space-y-6 lg:col-span-3">
          <AnalyticsSummaryCards summary={data.summary} />

          <ScoreTrendChart data={data.score_over_time} />

          <div className="grid gap-4 md:grid-cols-3">
            <MetricTrendChart
              title="Communication trend"
              subtitle="Daily average"
              data={data.communication_trend}
              color="hsl(var(--primary))"
            />
            <MetricTrendChart
              title="Confidence trend"
              subtitle="From speech analysis"
              data={data.confidence_trend}
              color="hsl(262 83% 58%)"
            />
            <MetricTrendChart
              title="Technical trend"
              subtitle="Answer technical scores"
              data={data.technical_trend}
              color="hsl(var(--accent))"
            />
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <WeakAreaFrequencyChart data={data.weak_area_frequency} />
            <InterviewHistoryChart history={data.interview_history} />
          </div>

          <RoleReadinessPanel items={data.role_readiness} />

          <ImprovementProgressPanel snapshot={data.improvement_progress} progress={progress} />

          <InterviewHistoryTable
            items={data.interview_history}
            page={data.interview_history_page}
            pages={data.interview_history_pages}
            total={data.interview_history_total}
            onPageChange={(page) => updateFilters({ page })}
          />
        </div>
      </div>
    </div>
  );
}
