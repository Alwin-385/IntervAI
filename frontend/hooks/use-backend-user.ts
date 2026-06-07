"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchMe } from "@/features/auth/api";
import { useAuthToken } from "@/hooks/use-auth-token";

export function useBackendUser() {
  const { getToken, isLoaded, isSignedIn } = useAuthToken();

  return useQuery({
    queryKey: ["me"],
    queryFn: () => fetchMe({ getToken }),
    enabled: isLoaded && isSignedIn,
    staleTime: 60_000,
    retry: 1,
  });
}
