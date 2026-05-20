"use client";

import { useBackendUser } from "@/hooks/use-backend-user";
import { WelcomeCard } from "@/features/dashboard/components/welcome-card";
import { StatsGrid } from "@/features/dashboard/components/stats-grid";
import { QuickActions } from "@/features/dashboard/components/quick-actions";
import { RecentActivity } from "@/features/dashboard/components/recent-activity";
import { AnalyticsPlaceholder } from "@/features/dashboard/components/analytics-placeholder";
import { WeakAreasPreview } from "@/features/dashboard/components/weak-areas-preview";

export function DashboardHome() {
  const { data: user, isLoading, isError, error } = useBackendUser();

  return (
    <div className="space-y-8 p-4 md:p-8">
      <WelcomeCard user={user} isLoading={isLoading} />

      {isError && (
        <p className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {(error as Error).message}
        </p>
      )}

      <StatsGrid isLoading={isLoading} />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <AnalyticsPlaceholder />
        </div>
        <QuickActions />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <RecentActivity isLoading={isLoading} />
        <WeakAreasPreview />
      </div>
    </div>
  );
}
