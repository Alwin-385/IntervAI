"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";

import { fetchSpeechSessionResults } from "@/features/speech/api";

export function useSpeechSessionResults(sessionId: string) {
  const { getToken, isLoaded, isSignedIn } = useAuth();

  return useQuery({
    queryKey: ["speech-session-results", sessionId],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return fetchSpeechSessionResults(token, sessionId);
    },
    enabled: isLoaded && isSignedIn && Boolean(sessionId),
    staleTime: 30_000,
  });
}
