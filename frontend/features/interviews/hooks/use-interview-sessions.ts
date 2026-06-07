"use client";

import { useQuery } from "@tanstack/react-query";

import { apiClient, ApiError } from "@/lib/api-client";
import type { InterviewSetupResponse } from "@/features/interviews/types";
import { useAuthToken } from "@/hooks/use-auth-token";

interface PaginatedSessions {
  items: InterviewSetupResponse[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export function useInterviewSessions(page = 1, pageSize = 20) {
  const { getToken, isLoaded, isSignedIn } = useAuthToken();

  return useQuery({
    queryKey: ["interview-sessions", page, pageSize],
    queryFn: () =>
      apiClient<PaginatedSessions>("/api/v1/interview-sessions/me", {
        getToken,
        params: { page: String(page), page_size: String(pageSize) },
      }),
    enabled: isLoaded && isSignedIn,
    staleTime: 5_000,
  });
}

export function useInterviewSession(sessionId: string) {
  const { getToken, isLoaded, isSignedIn } = useAuthToken();

  return useQuery({
    queryKey: ["interview-session", sessionId],
    queryFn: async () => {
      try {
        return await apiClient<InterviewSetupResponse>(`/api/v1/interview-sessions/${sessionId}`, {
          getToken,
        });
      } catch (err) {
        if (err instanceof ApiError && err.status === 404) return null;
        throw err;
      }
    },
    enabled: isLoaded && isSignedIn && Boolean(sessionId),
  });
}
