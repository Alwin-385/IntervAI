"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";

import { fetchSpeechCapabilities } from "@/features/speech/api";

export function useSpeechCapabilities() {
  const { getToken, isLoaded, isSignedIn } = useAuth();

  return useQuery({
    queryKey: ["speech-capabilities"],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return fetchSpeechCapabilities(token);
    },
    enabled: isLoaded && isSignedIn,
    staleTime: 60_000,
  });
}
