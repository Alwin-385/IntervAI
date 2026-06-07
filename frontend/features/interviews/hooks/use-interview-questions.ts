"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchInterviewQuestions } from "@/features/interviews/api";
import { useAuthToken } from "@/hooks/use-auth-token";

export function useInterviewQuestions(sessionId: string) {
  const { getToken, isLoaded, isSignedIn } = useAuthToken();

  return useQuery({
    queryKey: ["interview-questions", sessionId],
    queryFn: () => fetchInterviewQuestions({ getToken }, sessionId),
    enabled: isLoaded && isSignedIn && Boolean(sessionId),
    staleTime: 10_000,
  });
}
