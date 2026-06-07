import dynamic from "next/dynamic";

import { Skeleton } from "@/components/ui/skeleton";

const AnalyticsDashboardPage = dynamic(
  () =>
    import("@/features/analytics/components/analytics-dashboard-page").then(
      (m) => m.AnalyticsDashboardPage,
    ),
  {
    loading: () => (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-28 rounded-xl" />
          ))}
        </div>
        <Skeleton className="h-80 rounded-xl" />
      </div>
    ),
  },
);

export default function AnalyticsPage() {
  return (
    <div className="p-4 md:p-8">
      <AnalyticsDashboardPage />
    </div>
  );
}
