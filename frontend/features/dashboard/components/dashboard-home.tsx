"use client";

import { useBackendUser } from "@/hooks/use-backend-user";
import { WelcomeCard } from "@/features/dashboard/components/welcome-card";
import { StatsGrid } from "@/features/dashboard/components/stats-grid";
import { QuickActions } from "@/features/dashboard/components/quick-actions";
import { RecentActivity } from "@/features/dashboard/components/recent-activity";
import Link from "next/link";
import { BarChart3 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { WeakAreasPreview } from "@/features/dashboard/components/weak-areas-preview";
import { useDashboardOverview } from "@/features/dashboard/hooks/use-dashboard-overview";

export function DashboardHome() {
  const { data: user, isLoading: userLoading, isError, error } = useBackendUser();
  const {
    data: overview,
    isLoading: overviewLoading,
    isError: overviewError,
    error: overviewErr,
  } = useDashboardOverview();
  const isLoading = userLoading || overviewLoading;

  return (
    <div className="space-y-8 p-4 md:p-8">
      <WelcomeCard user={user} isLoading={isLoading} />

      {isError && (
        <p className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {(error as Error).message}
        </p>
      )}
      {overviewError && (
        <p className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {(overviewErr as Error).message}
        </p>
      )}

      <StatsGrid stats={overview?.stats} isLoading={isLoading} />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card className="glass-card h-full border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-primary" />
                Interview analytics
              </CardTitle>
              <CardDescription>
                Score trends, weak-area frequency, and role readiness
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button asChild variant="outline" className="w-full sm:w-auto">
                <Link href="/dashboard/analytics">Open analytics dashboard</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
        <QuickActions />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <RecentActivity
          items={overview?.recent_activity}
          isLoading={isLoading}
        />
        <WeakAreasPreview />
      </div>
    </div>
  );
}
