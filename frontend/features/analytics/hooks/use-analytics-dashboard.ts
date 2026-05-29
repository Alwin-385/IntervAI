"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";

import { fetchAnalyticsDashboard, fetchAnalyticsProgress } from "@/features/analytics/api";
import type { AnalyticsDashboardParams } from "@/features/analytics/types";

export function useAnalyticsDashboard(params: AnalyticsDashboardParams) {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  return useQuery({
    queryKey: ["analytics-dashboard", params],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return fetchAnalyticsDashboard(token, params);
    },
    enabled: isLoaded && isSignedIn,
    staleTime: 30_000,
  });
}

export function useAnalyticsProgress(
  params: Omit<AnalyticsDashboardParams, "page" | "page_size">,
) {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  return useQuery({
    queryKey: ["analytics-progress", params],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return fetchAnalyticsProgress(token, params);
    },
    enabled: isLoaded && isSignedIn,
    staleTime: 30_000,
  });
}
