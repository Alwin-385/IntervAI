"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { analyzeSpeech, fetchSpeechAnalysis } from "@/features/speech/api";
import type { SpeechAnalyzeRequest } from "@/features/speech/types";
import { useAuthToken } from "@/hooks/use-auth-token";

export function speechAnalysisKey(answerId: string) {
  return ["speech-analysis", answerId] as const;
}

export function useSpeechAnalysis(answerId: string | null) {
  const { getToken, isLoaded, isSignedIn } = useAuthToken();

  return useQuery({
    queryKey: speechAnalysisKey(answerId ?? ""),
    queryFn: () => {
      if (!answerId) throw new Error("Not authenticated");
      return fetchSpeechAnalysis({ getToken }, answerId);
    },
    enabled: isLoaded && isSignedIn && Boolean(answerId),
    retry: 1,
  });
}

export function useAnalyzeSpeech() {
  const { getToken } = useAuthToken();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: SpeechAnalyzeRequest) => analyzeSpeech({ getToken }, payload),
    onSuccess: (data) => {
      if (data.answer_id) {
        queryClient.setQueryData(speechAnalysisKey(data.answer_id), data);
      }
    },
  });
}
