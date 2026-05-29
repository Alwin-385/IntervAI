"use client";

import { useAuth } from "@clerk/nextjs";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { analyzeSpeech, fetchSpeechAnalysis, SpeechApiError } from "@/features/speech/api";
import type { SpeechAnalyzeRequest, SpeechAnalysisResult } from "@/features/speech/types";

export function speechAnalysisKey(answerId: string) {
  return ["speech-analysis", answerId] as const;
}

export function useSpeechAnalysis(answerId: string | null) {
  const { getToken, isLoaded, isSignedIn } = useAuth();

  return useQuery({
    queryKey: speechAnalysisKey(answerId ?? ""),
    queryFn: async () => {
      const token = await getToken();
      if (!token || !answerId) throw new Error("Not authenticated");
      return fetchSpeechAnalysis(token, answerId);
    },
    enabled: isLoaded && isSignedIn && Boolean(answerId),
    retry: (count, err) => {
      if (err instanceof SpeechApiError && err.status === 404) return false;
      return count < 1;
    },
  });
}

export function useAnalyzeSpeech() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: SpeechAnalyzeRequest) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return analyzeSpeech(token, payload);
    },
    onSuccess: (data) => {
      if (data.answer_id) {
        queryClient.setQueryData(speechAnalysisKey(data.answer_id), data);
      }
    },
  });
}
