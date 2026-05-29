"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";

import { fetchInterviewQuestions } from "@/features/interviews/api";

export function useInterviewQuestions(sessionId: string) {
  const { getToken, isLoaded, isSignedIn } = useAuth();

  return useQuery({
    queryKey: ["interview-questions", sessionId],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return fetchInterviewQuestions(token, sessionId);
    },
    enabled: isLoaded && isSignedIn && Boolean(sessionId),
    staleTime: 10_000,
  });
}
