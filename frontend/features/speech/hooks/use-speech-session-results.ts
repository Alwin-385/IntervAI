"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchSpeechSessionResults } from "@/features/speech/api";
import { useAuthToken } from "@/hooks/use-auth-token";

export function useSpeechSessionResults(sessionId: string) {
  const { getToken, isLoaded, isSignedIn } = useAuthToken();

  return useQuery({
    queryKey: ["speech-session-results", sessionId],
    queryFn: () => fetchSpeechSessionResults({ getToken }, sessionId),
    enabled: isLoaded && isSignedIn && Boolean(sessionId),
    staleTime: 30_000,
  });
}
