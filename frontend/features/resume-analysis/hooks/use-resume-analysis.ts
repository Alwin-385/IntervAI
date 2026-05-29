"use client";

import { useAuth } from "@clerk/nextjs";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  fetchResumeAnalysis,
  startResumeAnalysis,
} from "@/features/resume-analysis/api";
import type { ResumeAnalyzeRequest } from "@/features/resume-analysis/types";

export function analysisQueryKey(resumeId: string) {
  return ["resume-analysis", resumeId] as const;
}

export function useResumeAnalysis(resumeId: string) {
  const { getToken, isLoaded, isSignedIn } = useAuth();

  return useQuery({
    queryKey: analysisQueryKey(resumeId),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return fetchResumeAnalysis(token, resumeId);
    },
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
  const { getToken } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (body?: ResumeAnalyzeRequest) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return startResumeAnalysis(token, resumeId, body);
    },
    onSuccess: (data) => {
      queryClient.setQueryData(analysisQueryKey(resumeId), data);
    },
  });
}
