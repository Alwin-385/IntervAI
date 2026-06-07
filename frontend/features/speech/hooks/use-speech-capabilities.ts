"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchSpeechCapabilities } from "@/features/speech/api";
import { useAuthToken } from "@/hooks/use-auth-token";

export function useSpeechCapabilities() {
  const { getToken, isLoaded, isSignedIn } = useAuthToken();

  return useQuery({
    queryKey: ["speech-capabilities"],
    queryFn: () => fetchSpeechCapabilities({ getToken }),
    enabled: isLoaded && isSignedIn,
    staleTime: 60_000,
  });
}
