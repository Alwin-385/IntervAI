"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";

import { fetchDashboardOverview } from "@/features/dashboard/api";

export const DASHBOARD_QUERY_KEY = ["dashboard", "overview"] as const;

export function useDashboardOverview() {
  const { getToken, isLoaded, isSignedIn } = useAuth();

  return useQuery({
    queryKey: DASHBOARD_QUERY_KEY,
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return fetchDashboardOverview(token);
    },
    enabled: isLoaded && isSignedIn,
    staleTime: 5_000,
    refetchInterval: (query) => {
      const processing = query.state.data?.stats.resumes_processing ?? 0;
      return processing > 0 ? 2_000 : false;
    },
  });
}
