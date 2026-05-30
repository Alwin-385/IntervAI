"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useBackgroundJob } from "@/features/jobs/hooks/use-background-job";
import { fetchRoadmap, generateRoadmap, updateRoadmapItem } from "@/features/roadmap/api";

const QUERY_KEY = ["roadmap"];

export function useRoadmap(targetRole?: string) {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  return useQuery({
    queryKey: [...QUERY_KEY, targetRole ?? "all"],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return fetchRoadmap(token, targetRole);
    },
    enabled: isLoaded && isSignedIn,
    staleTime: 60_000,
  });
}

export function useGenerateRoadmap() {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const jobQuery = useBackgroundJob(activeJobId, Boolean(activeJobId));

  useEffect(() => {
    if (jobQuery.data?.status === "completed" && activeJobId) {
      qc.invalidateQueries({ queryKey: QUERY_KEY });
      setActiveJobId(null);
    }
    if (jobQuery.data?.status === "failed" && activeJobId) {
      setActiveJobId(null);
    }
  }, [jobQuery.data?.status, activeJobId, qc]);

  const mutation = useMutation({
    mutationFn: async (targetRole?: string) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return generateRoadmap(token, targetRole);
    },
    onSuccess: (data, targetRole) => {
      if (data.status === "processing" && data.job_id) {
        setActiveJobId(data.job_id);
        return;
      }
      qc.setQueryData([...QUERY_KEY, targetRole ?? "all"], data);
    },
  });

  return {
    ...mutation,
    isGenerating: mutation.isPending || Boolean(activeJobId),
    jobProgress: jobQuery.data?.progress_percent ?? 0,
    jobMessage: jobQuery.data?.progress_message ?? null,
  };
}

export function useUpdateRoadmapItem(roadmapId: string, targetRole?: string) {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ itemId, completed }: { itemId: string; completed: boolean }) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return updateRoadmapItem(token, roadmapId, itemId, completed);
    },
    onSuccess: (data) => qc.setQueryData([...QUERY_KEY, targetRole ?? "all"], data),
  });
}
