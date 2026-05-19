"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";

import { fetchMe } from "@/features/auth/api";

export function useBackendUser() {
  const { getToken, isLoaded, isSignedIn } = useAuth();

  return useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return fetchMe(token);
    },
    enabled: isLoaded && isSignedIn,
    staleTime: 60_000,
    retry: 1,
  });
}
