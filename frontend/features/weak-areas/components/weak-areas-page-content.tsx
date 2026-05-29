"use client";

import Link from "next/link";
import { Loader2, Mic, TrendingUp } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { WeakAreaCard } from "@/features/weak-areas/components/weak-area-card";
import { useWeakAreasAnalytics } from "@/features/weak-areas/hooks/use-weak-areas-analytics";

export function WeakAreasPageContent() {
  const { data, isLoading, isError, error } = useWeakAreasAnalytics();

  if (isLoading) {
    return (
      <div className="flex flex-col items-center gap-3 py-20">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-sm text-muted-foreground">Analyzing your interview history…</p>
      </div>
    );
  }

  if (isError || !data) {
    const message =
      error instanceof Error ? error.message : "Failed to load weak areas";
    return (
      <div className="space-y-3 rounded-xl border border-destructive/30 bg-destructive/10 p-4 text-sm">
        <p>{message}</p>
        {message.includes("Cannot reach") && (
          <p className="text-muted-foreground">
            Ensure Docker (Postgres) is running, then run{" "}
            <code className="rounded bg-muted px-1">.\scripts\start-backend.ps1</code> in another
            terminal.
          </p>
        )}
      </div>
    );
  }

  const { summary } = data;
  const hasHistory = summary.answers_analyzed > 0 || summary.speech_analyses_analyzed > 0;

  return (
    <div className="space-y-8">
      <div className="grid gap-4 md:grid-cols-2">
        <div className="glass-card rounded-2xl border border-primary/25 bg-primary/5 p-6">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Progress score
          </p>
          <p className="mt-2 text-4xl font-bold tabular-nums text-primary">
            {Math.round(summary.overall_improvement_score)}
            <span className="text-lg font-normal text-muted-foreground"> / 100</span>
          </p>
          <Progress value={summary.overall_improvement_score} className="mt-4 h-2" />
          <p className="mt-2 text-sm text-muted-foreground">
            Based on {summary.interviews_analyzed} interview(s), {summary.answers_analyzed} answer
            reviews, and {summary.speech_analyses_analyzed} speech analyses.
          </p>
        </div>

        <div className="glass-card rounded-2xl border border-border/50 p-6">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Priority breakdown
          </p>
          <ul className="mt-4 space-y-3 text-sm">
            <li className="flex justify-between">
              <span>High priority</span>
              <span className="font-semibold text-red-600 dark:text-red-400">
                {summary.high_priority_count}
              </span>
            </li>
            <li className="flex justify-between">
              <span>Medium priority</span>
              <span className="font-semibold text-amber-600 dark:text-amber-400">
                {summary.medium_priority_count}
              </span>
            </li>
            <li className="flex justify-between">
              <span>Low priority</span>
              <span className="font-semibold text-emerald-600 dark:text-emerald-400">
                {summary.low_priority_count}
              </span>
            </li>
          </ul>
          {data.trend_overview.length >= 2 && (
            <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
              <TrendingUp className="h-3.5 w-3.5" />
              Issue rate: {(data.trend_overview[0]!.rate * 100).toFixed(0)}% earlier →{" "}
              {(data.trend_overview[1]!.rate * 100).toFixed(0)}% recent
            </div>
          )}
        </div>
      </div>

      {data.personalized_recommendations.length > 0 && (
        <div className="glass-card rounded-xl border border-border/50 p-5">
          <p className="text-sm font-semibold">Personalized recommendations</p>
          <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
            {data.personalized_recommendations.map((rec) => (
              <li key={rec} className="rounded-md bg-muted/20 px-3 py-2">
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}

      {!hasHistory && (
        <div className="rounded-xl border border-dashed border-border/60 p-8 text-center">
          <p className="text-sm text-muted-foreground">
            Complete mock interviews and review results to detect recurring weak areas.
          </p>
          <Button asChild className="mt-4">
            <Link href="/dashboard/interviews/new">
              <Mic className="mr-2 h-4 w-4" />
              Start an interview
            </Link>
          </Button>
        </div>
      )}

      {data.weak_areas.length > 0 ? (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Recurring patterns</h2>
          <div className="grid gap-4 lg:grid-cols-2">
            {data.weak_areas.map((area, i) => (
              <WeakAreaCard key={area.kind} area={area} index={i} />
            ))}
          </div>
        </div>
      ) : hasHistory ? (
        <p className="text-sm text-muted-foreground">
          No recurring weaknesses detected yet — strong consistency across recent interviews.
        </p>
      ) : null}
    </div>
  );
}
