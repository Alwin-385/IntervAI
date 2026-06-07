"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchWeakAreasAnalytics } from "@/features/weak-areas/api";
import { useAuthToken } from "@/hooks/use-auth-token";

export function useWeakAreasAnalytics() {
  const { getToken, isLoaded, isSignedIn } = useAuthToken();

  return useQuery({
    queryKey: ["weak-areas-analytics"],
    queryFn: () => fetchWeakAreasAnalytics({ getToken }),
    enabled: isLoaded && isSignedIn,
    staleTime: 60_000,
  });
}
