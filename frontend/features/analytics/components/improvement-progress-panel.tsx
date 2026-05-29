"use client";

import { Progress } from "@/components/ui/progress";
import { ChartCard } from "@/features/analytics/components/chart-card";
import { MetricTrendChart } from "@/features/analytics/components/metric-trend-chart";
import type { AnalyticsProgress, ImprovementProgressSnapshot } from "@/features/analytics/types";

interface Props {
  snapshot: ImprovementProgressSnapshot;
  progress?: AnalyticsProgress;
}

export function ImprovementProgressPanel({ snapshot, progress }: Props) {
  return (
    <div className="space-y-4">
      <ChartCard title="Improvement progress" subtitle="Roadmap + weak-area momentum">
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <p className="text-xs text-muted-foreground mb-1">Roadmap completion</p>
            <div className="flex items-center gap-2">
              <Progress value={snapshot.roadmap_completion_rate} className="h-2 flex-1" />
              <span className="text-sm font-semibold">{snapshot.roadmap_completion_rate}%</span>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              {snapshot.roadmap_items_completed} / {snapshot.roadmap_items_total} tasks done
            </p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-1">Overall improvement index</p>
            <p className="text-2xl font-bold">
              {snapshot.overall_improvement_score != null
                ? `${snapshot.overall_improvement_score}%`
                : "—"}
            </p>
            <p className="mt-1 text-xs text-muted-foreground">
              {snapshot.weak_areas_improving} improving · {snapshot.weak_areas_declining} declining
              · {snapshot.weak_areas_high_priority} high priority
            </p>
          </div>
        </div>
      </ChartCard>

      {progress && (
        <div className="grid gap-4 lg:grid-cols-3">
          <MetricTrendChart
            title="Improvement score trend"
            data={progress.improvement_score_over_time}
            color="hsl(var(--primary))"
          />
          <MetricTrendChart
            title="Correctness trend"
            data={progress.correctness_over_time}
            color="hsl(142 76% 45%)"
          />
          <MetricTrendChart
            title="Roadmap completion trend"
            data={progress.roadmap_completion_over_time}
            color="hsl(var(--accent))"
          />
        </div>
      )}
    </div>
  );
}
