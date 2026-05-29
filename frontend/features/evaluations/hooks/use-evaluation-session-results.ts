"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";

import { fetchSessionAnswerEvaluations } from "@/features/evaluations/api";

export function useEvaluationSessionResults(
  sessionId: string,
  options?: { enabled?: boolean },
) {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const extraEnabled = options?.enabled ?? true;

  return useQuery({
    queryKey: ["answer-evaluation-session", sessionId],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return fetchSessionAnswerEvaluations(token, sessionId);
    },
    enabled: isLoaded && isSignedIn && Boolean(sessionId) && extraEnabled,
    staleTime: 30_000,
  });
}
