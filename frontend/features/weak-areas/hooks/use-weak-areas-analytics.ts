"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";

import { fetchWeakAreasAnalytics } from "@/features/weak-areas/api";

export function useWeakAreasAnalytics() {
  const { getToken, isLoaded, isSignedIn } = useAuth();

  return useQuery({
    queryKey: ["weak-areas-analytics"],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return fetchWeakAreasAnalytics(token);
    },
    enabled: isLoaded && isSignedIn,
    staleTime: 60_000,
  });
}
