"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchAnalyticsDashboard, fetchAnalyticsProgress } from "@/features/analytics/api";
import type { AnalyticsDashboardParams } from "@/features/analytics/types";
import { useAuthToken } from "@/hooks/use-auth-token";

export function useAnalyticsDashboard(params: AnalyticsDashboardParams) {
  const { getToken, isLoaded, isSignedIn } = useAuthToken();
  return useQuery({
    queryKey: ["analytics-dashboard", params],
    queryFn: () => fetchAnalyticsDashboard({ getToken }, params),
    enabled: isLoaded && isSignedIn,
    staleTime: 30_000,
    retry: 1,
    retryDelay: 4000,
  });
}

export function useAnalyticsProgress(
  params: Omit<AnalyticsDashboardParams, "page" | "page_size">,
  options?: { enabled?: boolean },
) {
  const { getToken, isLoaded, isSignedIn } = useAuthToken();
  const extraEnabled = options?.enabled ?? true;

  return useQuery({
    queryKey: ["analytics-progress", params],
    queryFn: () => fetchAnalyticsProgress({ getToken }, params),
    enabled: isLoaded && isSignedIn && extraEnabled,
    staleTime: 30_000,
    retry: 1,
    retryDelay: 5000,
  });
}
