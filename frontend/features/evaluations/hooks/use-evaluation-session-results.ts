"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchSessionAnswerEvaluations } from "@/features/evaluations/api";
import { useAuthToken } from "@/hooks/use-auth-token";

export function useEvaluationSessionResults(sessionId: string, options?: { enabled?: boolean }) {
  const { getToken, isLoaded, isSignedIn } = useAuthToken();
  const extraEnabled = options?.enabled ?? true;

  return useQuery({
    queryKey: ["answer-evaluation-session", sessionId],
    queryFn: () => fetchSessionAnswerEvaluations({ getToken }, sessionId),
    enabled: isLoaded && isSignedIn && Boolean(sessionId) && extraEnabled,
    staleTime: 30_000,
    retry: (count, error) => {
      const status = error && typeof error === "object" && "status" in error ? error.status : 0;
      return status === 401 && count < 1;
    },
  });
}
