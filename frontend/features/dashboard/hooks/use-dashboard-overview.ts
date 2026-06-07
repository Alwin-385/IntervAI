"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchDashboardOverview } from "@/features/dashboard/api";
import { useAuthToken } from "@/hooks/use-auth-token";

export const DASHBOARD_QUERY_KEY = ["dashboard", "overview"] as const;

export function useDashboardOverview() {
  const { getToken, isLoaded, isSignedIn } = useAuthToken();

  return useQuery({
    queryKey: DASHBOARD_QUERY_KEY,
    queryFn: () => fetchDashboardOverview({ getToken }),
    enabled: isLoaded && isSignedIn,
    staleTime: 30_000,
    refetchInterval: (query) => {
      const processing = query.state.data?.stats.resumes_processing ?? 0;
      return processing > 0 ? 5_000 : false;
    },
  });
}
