"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { fetchResumeAnalysis, startResumeAnalysis } from "@/features/resume-analysis/api";
import type { ResumeAnalyzeRequest } from "@/features/resume-analysis/types";
import { useAuthToken } from "@/hooks/use-auth-token";

export function analysisQueryKey(resumeId: string) {
  return ["resume-analysis", resumeId] as const;
}

export function useResumeAnalysis(resumeId: string) {
  const { getToken, isLoaded, isSignedIn } = useAuthToken();

  return useQuery({
    queryKey: analysisQueryKey(resumeId),
    queryFn: () => fetchResumeAnalysis({ getToken }, resumeId),
    enabled: isLoaded && isSignedIn && Boolean(resumeId),
    retry: 1,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "pending" || status === "processing") return 800;
      return false;
    },
  });
}

export function useStartResumeAnalysis(resumeId: string) {
  const { getToken } = useAuthToken();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body?: ResumeAnalyzeRequest) => startResumeAnalysis({ getToken }, resumeId, body),
    onSuccess: (data) => {
      queryClient.setQueryData(analysisQueryKey(resumeId), data);
    },
  });
}
